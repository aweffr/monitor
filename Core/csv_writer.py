# coding=utf-8

class CsvWriter:
    def __init__(self, name, path='./'):
        if name.find('txt') != -1:
            name = name.replace(u'txt', u'csv')
        else:
            name += u'.csv'
        self.f = open(path + name, 'w')
        self.filename = name

    def dict_to_csv(self, d):
        if d['LineNumber'] == 1:
            self.f.writelines(", ".join(d.keys()) + "\n")
        self.f.writelines(", ".join(map(str, d.values())) + "\n")

    def queue_dict_to_csv(self, q):
        for idx, d in enumerate(q):
            if idx == 0:
                self.f.writelines(", ".join(d.keys()) + "\n")
            else:
                self.dict_to_csv(d)

    def close(self):
        self.f.close()

    def flush(self):
        self.f.flush()


if __name__ == "__main__":
    d = {"LineNumber3": 1, "LineNumber2": 2, "LineNumber": 1}
    csv_f = CsvWriter('test')
    csv_f.dict_to_csv(d)
    csv_f.close()
