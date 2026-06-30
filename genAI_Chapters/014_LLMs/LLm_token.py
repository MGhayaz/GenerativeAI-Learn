import tiktoken
import google.genai as genai
encoding = tiktoken.get_encoding("o200k_base")
text = encoding.encode("irshard bhai ka meri hukmaran me khushamadid")
print(text)



