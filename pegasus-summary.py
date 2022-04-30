from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
import os
import json

src_text = []

model_name = "google/pegasus-billsum"
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
print("loaded tokenizer")
model = PegasusForConditionalGeneration.from_pretrained(model_name, length_penalty=3).to(device)
print("loaded model")

read_re = open('all_summaries.json')
result = json.load(read_re)
read_re.close()

for file in os.listdir("./sample_pdfs"):
    with open(f"./sample_pdfs/{file}") as f:
        if file[:-4] in result:
            print(f"Skipping {file}")
            continue
        print(f"Computing {file}")
        batch = tokenizer([f.read()], truncation=True, padding="longest", return_tensors="pt").to(device)
        translated = model.generate(**batch)
        tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
        result[file[:-4]] = tgt_text[0]
        wf = open('all_summaries.json', 'w+')
        json.dump(result, wf)
        wf.close()
