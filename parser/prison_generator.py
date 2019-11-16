def quote_key(key):
    """Quote a key string, if it contains a space."""
    if " " in key:
        return '"' + key + '"'
    return key


def generate(prison):
    """Generate a prison formatted output from a dict."""
    result = ""
    for key, value in prison.items():
        if isinstance(value, dict):
            recursive_string = generate(value)
            recursive_string = "    " + recursive_string.replace(
                "\n", "\n    "
            ).rstrip(" ")
            result += f"BEGIN {quote_key(key)}\n{recursive_string}END\n"
        else:
            result += f"{quote_key(key)} {value}\n"
    return result


if __name__ == "__main__":
    import json

    with open("example.prison.json", "r") as prison_file:
        text = "".join(prison_file.readlines())
        parsed = json.loads(text)
        print(generate(parsed))
