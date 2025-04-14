---
base_model: meta-llama/Llama-3.2-1B-Instruct
library_name: peft
---
# Test Case Prioritization Using LLMs for Regression Testing

This README provides instructions on how to run the `TSP_Fine_Tuning.py` file for fine-tuning a model for test case prioritization using the dataset from the apache commons project.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.7 or higher
- Required Python packages (listed in `requirements.txt`)

## Preparing the dataset

**If you already have the csv dataset in the correct format, you can skip this section.**

1. Download the common-collections source code from the following link:[common-collections](https://archive.apache.org/dist/commons/collections/source/) and extract the contents to a folder named `apache_commons` in the root directory of the project.

2. Run the RiskCalculation.java file on your apache_commons code to generate the dataset. The dataset will be saved as `risk_results.csv` in the `data` folder. A text version of the dataset will be generated in addition for readability.


## Preparing the Environment
1. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Model Access

The model used in this project is the `meta-llama/Llama-3.2-1B-Instruct` model. You can access it from the Hugging Face Model Hub.

1. Create a Hugging Face account if you don't have one.
    - Visit [Hugging Face](https://huggingface.co/) and sign up.
    - Verify your email address.
2. Go to the [Hugging Face website](https://huggingface.co/) and log in.

3. Navigate to the model page: [meta-llama/Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct).

4. Click on the "Access" button to get the model access token.

5. Copy the token and use it in your code to access the model.

6. Alternatively, you can use the `huggingface-cli` to log in:
    ```bash
    huggingface-cli login
    ```
7. Enter your token when prompted.


## Running the Fine-Tuning Script

To run the `TSP_Fine_Tuning.py` file, use the following command:

    ```bash
        python TSP_Fine_Tuning.py --data_path <path_to_data> --model_path <path_to_model> --output_path <path_to_save_fine_tuned_model>
    ```

### Arguments




### Framework versions

- PEFT 0.14.0