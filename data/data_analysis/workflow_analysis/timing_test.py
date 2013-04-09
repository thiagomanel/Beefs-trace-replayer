import unittest
from timing import *

class TestUpdate(unittest.TestCase):

    def assertStamp(self, entry, expected_begin, expected_elapsed):
        stamp = entry.clean_call.stamp()
        self.assertEquals(stamp[0], long(expected_begin))
        self.assertEquals(stamp[1], long(expected_elapsed))
    
    def testUpdate(self):
        lines = [
                 "{ \"args\": [ \"/home\", \"624640\", \"-1217757196\" ], \"call\": \"open\", \"caller\": { \"exec\": \"(automount)\", \"pid\": \"1102\", \"tid\": \"15603\", \"uid\": \"0\" }, \"children\": [ 2, 5, 5, 2 ], \"id\": 1, \"parents\": [], \"rvalue\": 18, \"stamp\": { \"begin\": 1319217042997604.0, \"elapsed\": 19 }}",
                 "{ \"args\": [ \"18\" ], \"call\": \"close\", \"caller\": { \"exec\": \"(automount)\", \"pid\": \"1102\", \"tid\": \"15603\", \"uid\": \"0\" }, \"children\": [], \"id\": 2, \"parents\": [ 1, 1 ], \"rvalue\": 0, \"stamp\": { \"begin\": 1319217042997675.0, \"elapsed\": 14 }}",
                 "{\"args\": [ \"/home/thiagoepdc/.gconf/apps/gnome-terminal/profiles\", \"624640\", \"-1217572876\" ], \"call\": \"open\", \"caller\": { \"exec\": \"(gnome-do)\", \"pid\": \"2076\", \"tid\": \"2194\", \"uid\": \"1159\" }, \"children\": [ 4, 150237, 4, 177440 ], \"id\": 3, \"parents\": [], \"rvalue\": 23, \"stamp\": { \"begin\": 1319217083956124.0, \"elapsed\": 19206 }}",
                 "{ \"args\": [ \"23\" ], \"call\": \"close\", \"caller\": { \"exec\": \"(gnome-do)\", \"pid\": \"2076\", \"tid\": \"2194\", \"uid\": \"1159\" }, \"children\": [ 150237 ], \"id\": 4, \"parents\": [ 3, 3 ], \"rvalue\": 0, \"stamp\": { \"begin\": 1319217083975523.0, \"elapsed\": 23 }}", 
                 "{ \"args\": [ \"/home\", \"624640\", \"-1217757196\" ], \"call\": \"open\", \"caller\": { \"exec\": \"(automount)\", \"pid\": \"1102\", \"tid\": \"15629\", \"uid\": \"0\" }, \"children\": [ 6, 94694, 94694, 6 ], \"id\": 5, \"parents\": [ 1, 1 ], \"rvalue\": 18, \"stamp\": { \"begin\": 1319217117019140.0, \"elapsed\": 18 }}",
                 "{ \"args\": [ \"18\" ], \"call\": \"close\", \"caller\": { \"exec\": \"(automount)\", \"pid\": \"1102\", \"tid\": \"15629\", \"uid\": \"0\" }, \"children\": [], \"id\": 6, \"parents\": [ 5, 5 ], \"rvalue\": 0, \"stamp\": { \"begin\": 1319217117019210.0, \"elapsed\": 22 }}",
                 "{ \"args\": [ \"/home/thiagoepdc/.config/google-chrome/Safe Browsing Bloom\", \"32834\", \"420\" ], \"call\": \"open\", \"caller\": { \"exec\": \"(chrome)\", \"pid\": \"16303\", \"tid\": \"16325\", \"uid\": \"1159\" }, \"children\": [ 8, 9, 8 ], \"id\": 7, \"parents\": [], \"rvalue\": 43, \"stamp\": { \"begin\": 1319217168627818.0, \"elapsed\": 587 }}",
                 "{ \"args\": [ \"/home/thiagoepdc/.config/google-chrome/Safe Browsing Bloom\", \"43\" ], \"call\": \"fstat\", \"caller\": { \"exec\": \"(chrome)\", \"pid\": \"16303\", \"tid\": \"16325\", \"uid\": \"1159\" }, \"children\": [ 9 ], \"id\": 8, \"parents\": [ 7, 7 ], \"rvalue\": 0, \"stamp\": { \"begin\": 1319217168628495.0, \"elapsed\": 78 }}",
                 "{ \"args\": [ \"/home/thiagoepdc/.config/google-chrome/Safe Browsing Bloom\", \"43\", \"0\", \"0\", \"SEEK_SET\" ], \"call\": \"llseek\", \"caller\": { \"exec\": \"(chrome)\", \"pid\": \"16303\", \"tid\": \"16325\", \"uid\": \"1159\" }, \"children\": [ 10, 12, 11, 10 ], \"id\": 9, \"parents\": [ 8, 7 ], \"rvalue\": 0, \"stamp\": { \"begin\": 1319217168628587.0, \"elapsed\": 5 }}"]

        entries = [WorkflowLine.from_json(json.loads(line)) for line in lines]
        workflow = {}
        for entry in entries:
            workflow[entry._id] = entry

        update(workflow)

        self.assertStamp(workflow[1], "1319217042997604", "19")
        self.assertStamp(workflow[2], str(1319217042997604 + 19), "14")#parent: 1
        self.assertStamp(workflow[3], "1319217083956124", "19206")
        self.assertStamp(workflow[4], str(1319217083956124 + 19206), "23")#parent: 3
        self.assertStamp(workflow[5], str(1319217042997604 + 19), "18")#parent: 1
        self.assertStamp(workflow[6], str(1319217042997604 + 19 + 18), "22")#parent: 5
        self.assertStamp(workflow[7], "1319217168627818", "587")

if __name__ == '__main__':
    unittest.main()
