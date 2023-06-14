import re
from faker import Faker

def anonymize(fp, out):
    """Anonymize a TSH file. Usefull for creating test cases
    Args: fp : a file like object that's use for input
          out: a file like object to which the results will be written
    """
    fake = Faker()

    for line in fp:
        if line and len(line) > 30 :
            line = line.strip()
            rating = re.search('[0-9]{1,4} ', line).group(0).strip()
            pos = line.index(rating)
            format = "{0:" + str(pos) +"s}{1}"
            print(format.format(fake.name(), line[pos:]), file=out)
