
# Project for CS_668 LLM 

### About this Repo: 
Dev Enviorment for my final project for the my LLM class. File contains test notebooks for processing my LLMs and playing around with the datasets needed for this project. 

### Project Goals:
Create a fine tuned LLM that is an expert on historical topics, that is capable of running on the RASPBERRY PI 5 with AI HAT + 2 offline. Goal of this project is to create a mini companion edge device 
that is capable of describing historical questions and topics to users. 

### Models Used:
Model that will be used has not been determined however will have to be a smaller model that is capable of running a constraint of 8GB of the AI HAT +2. Raspberry PI CPU needs to be able to run other processes such as frontend
application and handle inputted data from attached devices on the PI (Camera and Microphone). The model's available for this project are limited to the pre comiplied HEF formatted models from HAILO model zoo GENAI. 

These models are: 
	1. deepseek_r1/1.5b
	2. llama3.2/1b
	3. qwen2.5-coder/1.5b
	4. qwen2.5/1.5b
	5. qwen 2/1.5b 
	6. qwen 2/1.5b
	7. qwen3 

### Implementation Approach: 
	1. Use Curriclium Learning to fine tune a model to history domain. 
In this approach instead of fine tuning model on data that has data points treated as equal, I will introduce some sort of structure to the data.
By doing this I can establish some foundation knowledge for the model to have. This strucutre and division of dataset will have the data be divided out 
into different buckets where each bucket represents a different level of difficulty to data. 

	2. After having had finetuned model through some different stages of knowledge, I will use RAFT(Retrieval Augmented Fine Tuning) which combines RAG and 
fine tuning for better domain adaptation. This will be the final step of the model and will use the more comprhensive HIST-LLM dataset to attempt to answer harder 
historical questions. 
	3. Convert model to HEF format to run on HAILO device. 
 
https://apxml.com/courses/how-to-build-a-large-language-model/chapter-9-data-sampling-strategies-training/introduction-curriculum-learning
https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/raft-a-new-way-to-teach-llms-to-be-better-at-rag/4084674
https://www.youtube.com/watch?v=rqyczEvh3D4&time_continue=341&source_ve_path=NzY3NTg&embeds_referring_euri=https%3A%2F%2Fwww.google.com%2F
 
# Datasets Trained on: 

# Dataset 1 : World Important Events - Ancient to Modern
## Link: https://www.kaggle.com/datasets/saketk511/world-important-events-ancient-to-modern
### Description:
This dataset, "World Important Events - Ancient to Modern," spans significant historical milestones from ancient
times to the modern era, covering diverse global incidents. It provides a comprehensive timeline of events that
have shaped the world, offering insights into wars, cultural shifts, technological advancements, and social movements.



# Dataset 2 : A Manually Verified Dataset of Globally Famous Biographies
## Link: https://www.kaggle.com/datasets/saketk511/world-important-events-ancient-to-modern
### Description:
We present the Pantheon 1.0 dataset: a manually verified dataset of individuals that have transcended linguistic, 
temporal, and geographic boundaries. The Pantheon 1.0 dataset includes the 11,341 biographies present in more
than 25 languages in Wikipedia and is enriched with: (i) manually verified demographic information 
(place and date of birth, gender) (ii) a taxonomy of occupations classifying each biography at three 
levels of aggregation and (iii) two measures of global popularity including the number of languages in which
a biography is present in Wikipedia (L), and the Historical Popularity Index (HPI) a metric that combines 
information on L, time since birth, and page-views (2008-2013). We compare the Pantheon 1.0 dataset to data from the 2003 book, Human Accomplishments, and also to external measures of accomplishment in individual games and sports: Tennis, Swimming, Car Racing, and Chess. In all of these cases we find that measures of popularity (L and HPI) correlate highly with individual accomplishment, suggesting that measures of global popularity proxy the historical impact of individuals.



# Dataset 3: World History to 1500: Q&A Dataset
## Link: https://github.com/provos/world-history-to-1500-qa
### Description:
This dataset consists of high-quality question and answer pairs generated from the content of "World History Volume 1: to 1500".
The Q&A pairs are designed to cover key historical events, figures, and concepts from prehistory to 1500 CE, providing a comprehensive resource for students, educators, and history enthusiasts.


# Dataset 4: World History Since 1500: Q&A Dataset
## Link: https://github.com/provos/world-history-to-1500-qa
### Description:
This dataset consists of high-quality question and answer pairs generated from the content of "World History Since 1500: An Open and Free Textbook". The Q&A pairs are designed to cover key historical events, figures, and concepts from 1500 to the present day, providing a comprehensive resource for students, educators, and history enthusiasts.


## Model Finetuning Structure: 

| Experiment            | What it is                   | What changes                     |
| --------------------- | ---------------------------- | -------------------------------- |
| **A: Baseline**       | No training                  | Pure base model                  |
| **B: Mixed SFT**      | 1 LoRA adapter               | Trained on all datasets together |
| **C: Curriculum SFT** | 1 LoRA adapter (multi-stage) | Sequential training              |
| **D: QA-only SFT**    | 1 LoRA adapter               | Trained only on QA               |



## Training variable:
1. Base model
2. Mixed SFT LoRA
3. Curriculum LoRA
4. QA-only LoRA

## Hardware variable:
1. Raspberry Pi 16GB CPU-only
2. Raspberry Pi + Hailo-10H
3. A1000 GPU
4. RTX 4070 GPU
5. MacBook M2 Pro / M4 Pro
