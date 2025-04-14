import torch
import pandas as pd
import platform
from sklearn.preprocessing import MinMaxScaler
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Model Name
MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"

# Prompt user for CSV dataset path
CSV_DATASET_PATH = "C:/Users/jguzm/Research/Thesis Research/Llama_3_Fine_Tuning/Risk_results.csv"

# Check OS and adjust output directory accordingly
if platform.system() == "Windows":
    OUTPUT_DIR = r"C:\Users\jguzm\Research\Thesis Research\Llama_3_Fine_Tuning"
else:
    OUTPUT_DIR = "./fine_tuned_llama3_ranking"

df = pd.read_csv(CSV_DATASET_PATH)

# Generate Training Prompts
ranking_data = []
for i in range(len(df) - 1):
    func_high = df.iloc[i]
    func_low = df.iloc[i + 1]
    prompt = (
        f"Given the following Java functions, determine which one has a higher risk:\n\n"
        f"1. Function: {func_high['Method']} in {func_high['File']}\n"
        f"   - Cyclomatic Complexity: {func_high['Cyclomatic_Complexity']:.2f}\n"
        f"   - Lines of Code: {func_high['Lines_of_Code']:.2f}\n"
        f"   - Dependencies: {func_high['Dependencies']:.2f}\n"
        f"   - Inputs: {func_high['Inputs']:.2f}\n"
        f"   - Fan-In: {func_high['FanIn']:.2f}\n"
        f"   - Fan-Out: {func_high['FanOut']:.2f}\n"
        f"   - LCOM: {func_high['LCOM']:.2f}\n\n"
        f"2. Function: {func_low['Method']} in {func_low['File']}\n"
        f"   - Cyclomatic Complexity: {func_low['Cyclomatic_Complexity']:.2f}\n"
        f"   - Lines of Code: {func_low['Lines_of_Code']:.2f}\n"
        f"   - Dependencies: {func_low['Dependencies']:.2f}\n"
        f"   - Inputs: {func_low['Inputs']:.2f}\n"
        f"   - Fan-In: {func_low['FanIn']:.2f}\n"
        f"   - Fan-Out: {func_low['FanOut']:.2f}\n"
        f"   - LCOM: {func_low['LCOM']:.2f}\n\n"
        f"Answer: Function {func_high['Method']} has a higher risk score."
    )
    ranking_data.append({"text": prompt, "labels": 0})

# Convert ranking data to Hugging Face Dataset
ranking_dataset = Dataset.from_pandas(pd.DataFrame(ranking_data))

# Load Tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

# Tokenize Data
def preprocess_function(examples):
    inputs = tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
    inputs["labels"] = inputs["input_ids"].copy()
    return inputs

tokenized_datasets = ranking_dataset.map(preprocess_function, batched=True)

# Ensure correct device usage
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load Pretrained Model without offloading issues
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
    offload_folder=None  # Prevent offloading to disk
)

# LoRA Configuration for Efficient Fine-Tuning
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_proj", "v_proj"],  # Apply LoRA on attention layers
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model = prepare_model_for_kbit_training(model)

# Ensure model is in training mode
model.train()

# Ensure all parameters require gradients
for param in model.parameters():
    param.requires_grad = True

# Data Collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# Training Arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    evaluation_strategy="no",  # Disable evaluation
    save_strategy="epoch",
    learning_rate=2e-4,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=4,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    save_total_limit=2,
    fp16=True,  # Use mixed precision
    push_to_hub=False
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
    tokenizer=tokenizer,
    data_collator=data_collator
)

# Train the Model
trainer.train()

# Save Model
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Fine-tuning complete! Model saved to:", OUTPUT_DIR)