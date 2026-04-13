
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
 
### Datasets Trained on: 


HiST-LLM (History Seshat Test for LLMs): A dataset derived from the Seshat Global History Databank,
 containing over 36,000 data points across 600+ historical societies and 2,700+ scholarly references.
 It tests for expert-level knowledge from the Neolithic period to the Industrial Revolution.
