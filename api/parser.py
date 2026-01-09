import os
import xml.etree.ElementTree as ET
class TitleXMLParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.stack = []
        self.keys = {}
        self.dims = {}
        self._initialize()
    
    def _initialize(self):
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        self.stack.append(root)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.stack:
            raise StopIteration

        elem = self.stack.pop()
        t = elem.get('TYPE')
        n = elem.get('N')
        label = None

        if t in [ 'TITLE', 'CHAPTER', 'SUBCHAP', 'PART', 'SUBPART', 'SECTION']:
            for child in elem:
                if child.tag.startswith('HEAD'):
                    label = child.text
                    break
        
        # Update keys and dims
        type_map = {'TITLE': 'title', 'CHAPTER': 'chapter', 'SUBCHAP': 'subchapter', 'PART': 'part', 'SUBPART': 'subpart', 'SECTION': 'section'}
        if t in type_map:
            key = type_map[t]
            self.dims[key] = label
            self.keys[key] = f"{n}"
        
        # Add child DIV elements to queue
        for child in elem:
            if child.tag.startswith('DIV'):
                self.stack.append(child)
                
        if t == 'SECTION':
            paragraphs = ' '.join(''.join(p.itertext()) for p in elem.findall('.//P'))
            return {'dims': self.dims.copy(), 'keys': self.keys.copy(), 'text': paragraphs}
        
        return self.__next__()

def main():
    file_path = 'api/xml_data/title1/title-1_2015-12-18.xml'
    
    curent_dir = os.getcwd()
    file_path = os.path.join(curent_dir, file_path)
    rows = TitleXMLParser(file_path)
   # Process the parsed rows as needed
    for row in rows:
        print(row)
        # wait to keystroke to continue
        input()
if __name__ == '__main__':    main()    
