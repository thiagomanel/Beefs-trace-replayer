import sys

if __name__ == "__main__":

    def print_element(element):
        sys.stdout.write(" ".join(element[:-1]) + "}\n")

    lines = sys.stdin.readlines()
    #removing special chars
    del lines[0]
    del lines[-1]

    element = []
    outlines = []
    for line in lines:
        token = line.strip()
        if token == "{":
            if element:#previous element
                outlines.append(element)
            element = []
        element.append(token)
    outlines.append(element)

    sys.stdout.write(str(len(outlines)) + "\n")
    for out in outlines:
        print_element(out)
