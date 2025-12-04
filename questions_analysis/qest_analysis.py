# =============================================================================
# QUESTION ANALYSIS FUNCTIONS - UPDATED
# =============================================================================

def analisar_questao_com_professor_ia(texto_questao, disciplina, conteudo, contexto_aluno, numero_questao, OPENAI_AVAILABLE, openai, st, os):
    """Complete analysis with option to consult AI Professor"""
    
    # First, basic analysis
    if OPENAI_AVAILABLE:
        try:
            from openai import OpenAI
            
            # Get API key
            api_key = None
            if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
                api_key = st.session_state.openai_api_key
            elif 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
            else:
                api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                raise Exception("API key not available")
            
            client = OpenAI(api_key=api_key)
            
            prompt = f"""
            You are a {disciplina} tutor specialized for high school. 
            
            QUESTION {numero_questao} - {conteudo}:
            {texto_questao[:1500]}
            
            STUDENT CONTEXT: {contexto_aluno['nome']} has difficulty in {contexto_aluno['conteudos_port'][:1] if contexto_aluno['conteudos_port'] else 'some contents'}
            
            Provide an initial analysis that:
            1. Identifies what the question is asking
            2. Highlights the main concepts of {conteudo}
            3. Suggests a solving strategy
            4. Indicates where the student might have doubts
            
            Be clear and direct. Use maximum 400 words.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a specialized tutor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            analise_basica = response.choices[0].message.content.strip()
            
        except:
            analise_basica = f"""
            **🔍 Analysis of Question {numero_questao} - {disciplina}**
            
            **Content:** {conteudo}
            
            **What to do:**
            1. Read the statement carefully
            2. Identify what is being asked
            3. Recall the concepts of {conteudo}
            4. Apply knowledge in the solution
            
            **Tip:** Use AI Professor (button below) to ask specific questions about this question!
            """
    else:
        analise_basica = f"""
        **🔍 Question {numero_questao} - {conteudo} ({disciplina})**
        
        This question addresses {conteudo}. 
        
        **For a detailed analysis with AI Professor, configure OpenAI in the settings menu.**
        
        Meanwhile:
        1. Review the concept of {conteudo}
        2. Consult the recommended lesson
        3. Practice with similar exercises
        """
    
    return analise_basica




from questions_analysis.qest_analysis import analisar_questao_com_professor_ia