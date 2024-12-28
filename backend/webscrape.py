from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://www.investorgain.com/report/live-ipo-gmp/331/ipo/")

docs = loader.load()

metadata = docs[0].metadata

content = docs[0].page_content

index = content.find("GMP Updated")
last_index = content.find("What is")

new_content = content[index+11:last_index].strip()

print(new_content)

with open("../ipo_gmp.text", "w") as file:
    file.write(new_content)