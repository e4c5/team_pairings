import re
from faker import Faker

def anonymize(in_file, out_file):
    fake = Faker()

    with open(in_file) as fp:
        with open(out_file, "w") as out:
            for line in fp:
                if line and len(line) > 30 :
                    line = line.strip()
                    rating = re.search('[0-9]{1,4} ', line).group(0).strip()
                    pos = line.index(rating)
                    format = "{0:" + str(pos) +"s}{1}"
                    print(format.format(fake.name(), line[pos:]), file=out)

            
if __name__ == '__main__':
    anonymize('/home/raditha/SLSL/tsh/2020/SOY1/a.t','/workspaces/python/team_pair/tsh/data/tournament1/a.t')