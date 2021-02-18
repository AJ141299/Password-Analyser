import requests
import hashlib
import sys
import os


def request_api_data(query_char: str):
    """Calls the API and receives the response.

    Args:
        query_char (str): First five characters of SHA1 hashed password.

    Raises:
        RuntimeError: If the response from the API is anything other than 200.

    Returns:
        response: The response from the API.
    """

    url = 'https://api.pwnedpasswords.com/range/' + query_char
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError(
            f"Error fetching: error {response.status_code}, check the api and try again.")

    return response


def get_password_leaks_count(hashes, hash_to_check: str) -> int:
    """Checks the password hash against the response hashes and returns the count.

    Args:
        hashes: Response object containing the hashes.
        hash_to_check (str): Password hash to check against the received hashes.

    Returns:
        count (int): The number of times the password was found.
    """

    hashes = (line.split(":") for line in hashes.text.splitlines())
    for hash, count in hashes:
        if hash == hash_to_check:
            return count
    return 0


def pwned_api_check(password: str) -> int:
    """Converts the password into SHA1 hash and uses K-anonymity to receive response from the API. The response object is checked to find a match for the given password.

    Args:
        password (str): Password to check.

    Returns:
        count (int): The number of times the password was found.
    """

    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

    first5_chars, tail = sha1password[:5], sha1password[5:]  # for K-anonymity
    response = request_api_data(first5_chars)

    count = get_password_leaks_count(response, tail)
    return count


def main(password: str):
    """Main function that runs the program. Prints the number of times the password was found.

    Args:
        password (str): Password to check.
    """

    count = pwned_api_check(password)
    if count:
        print(
            f"{password} was found {count} times. You should change your password!")
    else:
        print(f"{password} was NOT found. Carry on!")


if __name__ == "__main__":
    # reads passwords from a file and then deletes them
    with open(
            os.path.join(sys.path[0], "passwords.txt"), "r+") as file:
        passwords = file.readlines()

        if not passwords:
            print("Passwords file is empty!")
        else:
            print("Checking passwords...")
            for password in passwords:
                password = password.splitlines()[0]  # to remove "\n"
                main(password)
            file.truncate(0) # clears the file
