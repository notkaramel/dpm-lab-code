import pyperclip
import sys


def input_line():
    return parse_line(input("Input: "))


def parse_line(original):
    line = list(map(str.strip, original.split(':')))
    keys = ",".join([f"\"{key.strip()}\"" for key in line[1].split(',')])
    text = (f'"{line[0]}" : [{keys}],')
    return text


def main():
    iterations = int(sys.argv[1])
    print(iterations)
    text = ""
    while iterations > 0:
        iterations -= 1
        text += input_line() + '\n'
        print("Output to Clipboard:", text.strip(), sep="\n")
        pyperclip.copy(text)


def file_main():
    filename = sys.argv[1]
    print(">>> Processing", filename)
    with open(filename, 'r') as f:
        lines = list(map(parse_line, map(str.strip, f.readlines())))
        text = "\n".join(lines)
        pyperclip.copy(text)
        print("Output:", text, sep='\n')


if __name__ == '__main__':
    file_main()
