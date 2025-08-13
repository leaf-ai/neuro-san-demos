import autogen
from coded_tools.healthcare_assistant.tools.healthcare_tools import AppointmentScheduler, MedicationManager, HealthKnowledgeBase

class HealthcareMultiAgentSystem:
    def __init__(self, config):
        """Initialize the Healthcare Multi-Agent System with HOCON configuration."""
        self.config = config
        self.appointment_scheduler = AppointmentScheduler()
        self.medication_manager = MedicationManager()
        self.health_kb = HealthKnowledgeBase()
        
        # Initialize agents with HOCON config
        self.scheduler_agent = autogen.AssistantAgent(
            name="SchedulerAgent",
            system_message=config["healthcare_assistant.agents.scheduler_agent.system_message"],
            llm_config=config["healthcare_assistant.agents.scheduler_agent.llm_config"]
        )
        self.medication_agent = autogen.AssistantAgent(
            name="MedicationAgent",
            system_message=config["healthcare_assistant.agents.medication_agent.system_message"],
            llm_config=config["healthcare_assistant.agents.medication_agent.llm_config"]
        )
        self.health_advisor = autogen.AssistantAgent(
            name="HealthAdvisor",
            system_message=config["healthcare_assistant.agents.health_advisor_agent.system_message"],
            llm_config=config["healthcare_assistant.agents.health_advisor_agent.llm_config"]
        )
        self.coordinator = autogen.AssistantAgent(
            name="Coordinator",
            system_message=config["healthcare_assistant.agents.coordinator_agent.system_message"],
            llm_config=config["healthcare_assistant.agents.coordinator_agent.llm_config"]
        )
        
        # Register functions with agents
        self.register_functions()
    
    def register_functions(self):
        """Register healthcare functions with appropriate agents."""
        @self.scheduler_agent.register_for_execution()
        @self.coordinator.register_for_llm(name="schedule_appointment", description="Schedule medical appointments")
        def schedule_appointment(patient_id: str, doctor_id: str, preferred_date: str, appointment_type: str):
            return self.appointment_scheduler.schedule_appointment(patient_id, doctor_id, preferred_date, appointment_type)
        
        @self.medication_agent.register_for_execution()
        @self.coordinator.register_for_llm(name="add_medication", description="Add medication reminders")
        def add_medication(patient_id: str, medication: dict):
            return self.medication_manager.add_medication(patient_id, medication)
        
        @self.medication_agent.register_for_execution()
        @self.coordinator.register_for_llm(name="get_medication_reminders", description="Get medication reminders")
        def get_medication_reminders(patient_id: str):
            return self.medication_manager.get_medication_reminders(patient_id)
        
        @self.health_advisor.register_for_execution()
        @self.coordinator.register_for_llm(name="get_health_tips", description="Get health tips")
        def get_health_tips(category: str = "general"):
            return self.health_kb.get_health_tips(category)

    def start_conversation(self, user_message: str):
        """Start a conversation with the healthcare system."""
        user_proxy = autogen.UserProxyAgent(
            name="Patient",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False
        )
        
        # Create group chat
        groupchat = autogen.GroupChat(
            agents=[user_proxy, self.coordinator, self.scheduler_agent, 
                   self.medication_agent, self.health_advisor],
            messages=[],
            max_round=10
        )
        
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config=self.config["healthcare_assistant.agents.coordinator_agent.llm_config"]
        )
        
        # Start the conversation
        user_proxy.initiate_chat(manager, message=user_message)