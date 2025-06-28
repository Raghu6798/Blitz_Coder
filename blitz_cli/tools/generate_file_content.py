from langchain_core.tools import tool
from langchain.prompts import ChatPromptTemplate

@tool
def generate_file_content(
    framework: str,
    use_case: str,
    file_path: str,
    purpose: str = "Core application file",
    features: str = "",
    architecture_overview: str = "",
    data_flow: str = "",
    dependencies: str = "[]",
) -> str:
    """
    Generate content for a specific file based on the architecture plan and project context.
    Returns the code as a string.
    """
    system_prompt = """You are an expert software developer specializing in production-ready, scalable applications. Generate code for the specified file following modern best practices and patterns, regardless of programming language or framework.\n\n**PROJECT CONTEXT:**\nFramework: {framework}\nUse Case: {use_case}\nFile: {file_path}\nPurpose: {purpose}\nKey Features: {features}\n\n**COMPLETE PROJECT ARCHITECTURE:**\n{architecture_overview}\n\n**COMPONENT RELATIONSHIPS:**\n{data_flow}\n\n**FILE DEPENDENCIES:**\n{dependencies}\n\n---\n\n**3. SECURITY BEST PRACTICES:**\n- Implement proper authentication/authorization if applicable\n- Use secure password handling where relevant\n- Implement secure token handling if needed\n- Use proper CORS configuration for web APIs\n- Input validation and sanitization\n\n**4. CODE QUALITY:**\n- Type annotations or equivalents and proper documentation\n- Clean code principles\n- Proper error handling\n- Logging and monitoring\n- Unit test coverage\n- Performance optimization\n\n**5. PROJECT STRUCTURE:**\n- Modular and maintainable code\n- Clear separation of concerns\n- Dependency injection where appropriate\n- Configuration management\n- Environment variable handling\n\n---\n**🎯 FINAL INSTRUCTIONS:**\n\nGenerate ONLY the complete, production-ready code for: **{file_path}**\n\nRequirements:\n1. Follow all architectural patterns above\n2. Include proper type annotations or equivalents\n3. Add comprehensive documentation\n4. Include proper error handling\n5. Ensure proper imports or dependencies\n6. Add logging where appropriate\n\nDo not include explanations or text outside the code block."""
    content_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "Write the complete, production-ready code for {file_path}"),
        ]
    )
    messages = content_prompt.format_messages(
        framework=framework,
        use_case=use_case,
        file_path=file_path,
        purpose=purpose,
        features=features,
        architecture_overview=architecture_overview,
        data_flow=data_flow,
        dependencies=dependencies,
    )
    # result = mistral_small.invoke(messages)
    # match = re.search(r"```(?:python)?\s*([\s\S]*?)```", result.content, re.DOTALL)
    # return match.group(1).strip() if match else result.content.strip()
    return f'framework:{framework} , use_case:{use_case},file_path:{file_path},purpose: {purpose},features: {features},architecture_overview: {architecture_overview},data_flow:{data_flow},dependencies:{dependencies}'

if __name__ == "__main__":
    generate_file_content()
