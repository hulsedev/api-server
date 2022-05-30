import sys, re
import dotenv

regex_pattern = """([a-z-0-9]){20,}\w+"""

if __name__ == "__main__":
    input_file, output_file = sys.argv[1], sys.argv[2]
    with open(input_file, "r") as f:
        log = f.read()

    # extract token from newly generated log file
    token = re.search(regex_pattern, log).group(0)
    dotenv.set_key(output_file, "MOCK_API_KEY", token)
