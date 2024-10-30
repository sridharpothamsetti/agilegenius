from langchain.agents import tool
from langchain.chat_models import ChatOpenAI
from crewai import Agent, Task, Process, Crew
from crewai.project import agent, task, crew, CrewBase
import yaml
from dotenv import load_dotenv
import os
import pandas as pd  # Ensure pandas is imported if not already
from databricks.vector_search.client import VectorSearchClient  # Replace with actual module import for VectorSearchClient
load_dotenv()
class AgileCrew:
    def __init__(self):
        
        # Load agent and task configurations from YAML files
        with open('config/agents.yaml') as f:
            self.agents_config = yaml.safe_load(f)
        with open('config/tasks.yaml') as f:
            self.tasks_config = yaml.safe_load(f)


        # Set up Databricks LLM
        self.databricks_llm = ChatOpenAI(
            model="databricks/databricks-mixtral-8x7b-instruct",
            base_url="https://dbc-105d4356-38a7.cloud.databricks.com/serving-endpoints/databricks-mixtral-8x7b-instruct/invocations",
            openai_api_key=os.getenv('DATABRICKS_TOKEN') 
        )
        self.endpoint_name = "genai_vs_endpoint"
        self.index_name = "agentic_rag_prod.product.user_story_index"

    @tool
    def vs(self, query):
        """Vector Search Tool"""
        vsc = VectorSearchClient( disable_notice=True)
        index = vsc.get_index(endpoint_name=self.endpoint_name, index_name=self.index_name)
        data_columns = ["id", "content"]
        results = index.similarity_search(query_text=query, columns=data_columns, num_results=1)
        result_columns = [c["name"] for c in results["manifest"]["columns"]]
        search_results_df = pd.DataFrame(results['result']['data_array'], columns=result_columns)
        return search_results_df['content'][0]


    def product_owner(self):
        return Agent(
            config=self.agents_config['product_owner'],
            llm=self.databricks_llm
        )


    def scrum_master(self):
        return Agent(
            config=self.agents_config['scrum_master'],
            llm=self.databricks_llm
        )


    def project_manager(self):
        return Agent(
            config=self.agents_config['project_manager'],
            llm=self.databricks_llm
        )


    def task_backlog_prioritization(self):
        return Task(
            config=self.tasks_config['task_backlog_prioritization'],
            tool=[self.vs],
            agent=self.product_owner()
        )


    def task_facilitate_meetings(self):
        return Task(
            config=self.tasks_config['task_facilitate_meetings'],
            context=[self.task_backlog_prioritization()],
            agent=self.scrum_master()
        )


    def task_resource_allocation(self):
        return Task(
            config=self.tasks_config['task_resource_allocation'],
            context=[self.task_facilitate_meetings()],
            agent=self.project_manager(),
        )


    def crew(self):
        return Crew(
            agents=[self.product_owner(), self.scrum_master(), self.project_manager()],
            tasks=[self.task_backlog_prioritization(), self.task_facilitate_meetings(), self.task_resource_allocation()],
            verbose=True,
            process=Process.sequential,
        )
