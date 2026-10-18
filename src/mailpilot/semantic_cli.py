import argparse
from pathlib import Path
from .semantic import classify_file
def main():
    p=argparse.ArgumentParser(description="Classify cached Gmail metadata with local Ollama")
    p.add_argument("--account",choices=["account1","account2","both"],default="both")
    p.add_argument("--limit",type=int,default=100)
    p.add_argument("--model",default="qwen2.5:3b")
    a=p.parse_args()
    if a.limit<1:p.error("--limit must be positive")
    for account in (["account1","account2"] if a.account=="both" else [a.account]):
        print(classify_file(Path.cwd(),account,a.limit,a.model))
if __name__=="__main__":main()
