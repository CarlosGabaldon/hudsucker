
class TCPServiceResponse(object):
    """
    Parses response's from the Hudsucker TCP service
    
    :content: content of response
    """
    def __init__(self, data):
        self.data = data
        self.response_code = '200'
        self.content = None
        self.parse_response(data)
    
    def is_success(self):
        """Tests whether the response was successful"""
        if self.response_code in ['200']:
            return True
        else:
            return False
    
    def parse_response(self,data):
        """Create a clone of this service definition"""
        #print 'parsing data:  %s' % data
        lines = [line for line in data.split('\r\n')]
        if len(lines[0]) > 4:
            # Legacy format before versioning
            # format:    0210some_value
            #    02 = 2 bytes for length of '10' (10 bytes = length of 'some_value')
            content_len_bytes = int(data[:2])
            meta_length = content_len_bytes + 2
            content_length = int(data[2:content_len_bytes + 2])
            self.content = str(data[meta_length:meta_length + content_length])
        elif lines[0] == 'v1.0':
            self.response_code = lines[1]
            meta_len = len('v1.0\r\n%s\r\n%s\r\n' % (lines[1],lines[2]))
            content_length = int(lines[2])
            if self.is_success():
                self.content = data[meta_len : meta_len + content_length]
            else:
                return
        else:
            if data == '':
                self.response_code = '500'
                return
            raise Exception('Format not supported')
    

