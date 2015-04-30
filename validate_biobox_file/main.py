import argparse
import yaml
import yaml.scanner as scan
import os.path
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
from pymonad.Either import Left, Right
from pymonad.Reader import curry

# This imports the * and & operators for monads
from pymonad.Applicative import *


def generate_exit_status(result):
    is_error = (result.__class__ == Left)
    if is_error:
        return (1, result.getValue() + "\n")
    else:
        return (0, "")

def get_arguments():
    parser = argparse.ArgumentParser(
            description='Validates the input data for a biobox.')
    parser.add_argument('--schema', '-s', dest='schema_file', required=True)
    parser.add_argument('--input',  '-i', dest='input_file',  required=True)
    return vars(parser.parse_args())

def parse_yaml(file_):
    try:
        with open(file_, "r") as f:
            return Right(yaml.load(f.read()))
    except scan.ScannerError:
        return Left("Error parsing the YAML file: {0}".format(file_))
    except IOError:
        return Left("File not found: {0}".format(file_))

@curry
def validate(schema, input_):
    validator = Draft4Validator(schema)
    if(validator.is_valid(input_)):
        return Right(input_)
    else:
        error = best_match(Draft4Validator(schema).iter_errors(input_))
        return Left(error.message)


def check_mounted_files(input_):

    def is_file_arg(arg):
        file_types = ["fastq","fasta"]
        return any(map(lambda x: x in arg.keys(), file_types))

    def validate_file_arg(arg):
        if arg.__class__ == list:
            return map(validate_file_arg, arg)
        else:
            if not os.path.isfile(arg["value"]):
                msg = "Provided path '{0}' in item '{1}' does not exist."
                return Left(msg.format(arg["value"], arg["id"]))
            else:
                return Right("This message is never propogated to user.")

    def resolve(x, y):
        if y.__class__ == list:
            return reduce(resolve, y, x) >> x
        else:
            return y >> x

    file_args   = filter(is_file_arg, input_['arguments'])
    file_states = map(lambda x: validate_file_arg(x.values()), file_args)
    return reduce(resolve, file_states, Right(input_))


def run():
    args  = get_arguments()
    chain = [validate,
             parse_yaml(args['schema_file']),
             parse_yaml(args['input_file'])]

    result = reduce(lambda method, result: result >> method, chain) >> check_mounted_files

    return generate_exit_status(result)
