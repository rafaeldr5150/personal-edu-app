# =============================================================================
# GAMIFICATION SYSTEM
# =============================================================================

from datetime import datetime

def inicializar_sistema_gamificacao(st):
    """Initializes gamification system in session"""
    if 'gamificacao' not in st.session_state:
        st.session_state.gamificacao = {
            'pontos': 0,
            'nivel': 1,
            'conquistas': [],
            'streak_dias': 0,
            'ultimo_acesso': datetime.now().strftime("%Y-%m-%d"),
            'questoes_revisadas': 0,
            'metas_concluidas': 0,
            'perguntas_professor': 0,
            'dias_estudando': 0
        }

def verificar_conquistas(aluno_data, st):
    """Checks and awards achievements based on performance"""
    # Dictionary mapping achievements to their points
    conquistas_pontos = {
        "King of Portuguese": 50,
        "Portuguese Master": 30,
        "Portuguese Aspirant": 15,
        "King of Mathematics": 50,
        "Mathematics Master": 30,
        "Mathematics Aspirant": 15,
        "Perfection!": 100,
        "Focus on Weaknesses": 40,
        "In Progress": 20,
        "Perfect Balance": 25
    }
    
    conquistas = []
    
    # ===== ACHIEVEMENTS BY CORRECT ANSWERS =====
    if aluno_data['acertos_port'] >= 18:
        conquistas.append({"emoji": "👑", "nome": "King of Portuguese", "descricao": "18/18 correct in Portuguese"})
    elif aluno_data['acertos_port'] >= 15:
        conquistas.append({"emoji": "🎯", "nome": "Portuguese Master", "descricao": "15+ correct in Portuguese"})
    elif aluno_data['acertos_port'] >= 12:
        conquistas.append({"emoji": "📚", "nome": "Portuguese Aspirant", "descricao": "12+ correct in Portuguese"})
    
    if aluno_data['acertos_mat'] >= 18:
        conquistas.append({"emoji": "👑", "nome": "King of Mathematics", "descricao": "18/18 correct in Mathematics"})
    elif aluno_data['acertos_mat'] >= 15:
        conquistas.append({"emoji": "🧮", "nome": "Mathematics Master", "descricao": "15+ correct in Mathematics"})
    elif aluno_data['acertos_mat'] >= 12:
        conquistas.append({"emoji": "📐", "nome": "Mathematics Aspirant", "descricao": "12+ correct in Mathematics"})
    
    # ===== ACHIEVEMENTS BY REVIEW =====
    total_questoes_revisar = len(aluno_data['erros_port_df']) + len(aluno_data['erros_mat_df'])
    if total_questoes_revisar == 0:
        conquistas.append({"emoji": "🌟", "nome": "Perfection!", "descricao": "No errors in any question"})
    elif total_questoes_revisar <= 3:
        conquistas.append({"emoji": "💪", "nome": "Focus on Weaknesses", "descricao": "Reviewing errors with determination"})
    elif total_questoes_revisar <= 8:
        conquistas.append({"emoji": "📖", "nome": "In Progress", "descricao": "Reviewing questions to improve"})
    
    # ===== BALANCE ACHIEVEMENT =====
    if aluno_data['acertos_port'] >= 10 and aluno_data['acertos_mat'] >= 10:
        conquistas.append({"emoji": "⚖️", "nome": "Perfect Balance", "descricao": "Good performance in both subjects"})
    
    # ===== ADD NEW ACHIEVEMENTS TO SESSION =====
    for conquista in conquistas:
        nome = conquista.get('nome')
        nomes_existentes = [c.get('nome') for c in st.session_state.gamificacao['conquistas']]
        
        if nome not in nomes_existentes:
            st.session_state.gamificacao['conquistas'].append(conquista)
            pontos = conquistas_pontos.get(nome, 10)
            st.session_state.gamificacao['pontos'] += pontos
            print(f"✅ Achievement unlocked: {nome} (+{pontos} points)")
    
    return conquistas

def atualizar_pontuacao(acao, detalhes=None, st=None):
    """Updates score based on user actions"""
    pontos_acao = {
        'revisao_questao': 5,
        'conclusao_meta': 15,
        'acesso_diario': 2,
        'conquista': 10,
        'pergunta_professor': 8,
        'interacao_lu': 3,
        'completou_aba': 20
    }
    
    if acao in pontos_acao:
        pontos = pontos_acao[acao]
        st.session_state.gamificacao['pontos'] += pontos
        
        # Update level (every 50 points)
        st.session_state.gamificacao['nivel'] = st.session_state.gamificacao['pontos'] // 50 + 1
        
        # Count specific actions
        if acao == 'revisao_questao':
            st.session_state.gamificacao['questoes_revisadas'] += 1
        elif acao == 'pergunta_professor':
            st.session_state.gamificacao['perguntas_professor'] += 1
        elif acao == 'conclusao_meta':
            st.session_state.gamificacao['metas_concluidas'] += 1

def exibir_widget_gamificacao(st):
    """Displays gamification widget with points, level and progress"""
    gami = st.session_state.gamificacao
    
    # Colors by level
    cores_nivel = {
        1: '#4f46e5',  # Blue
        2: '#8b5cf6',  # Purple
        3: '#d946ef',  # Magenta
        4: '#ec4899',  # Pink
        5: '#f43f5e',  # Red
    }
    
    nivel_atual = gami['nivel']
    cor = cores_nivel.get(min(nivel_atual, 5), '#4f46e5')
    
    # Calculate progress to next level
    pontos_atuais = gami['pontos']
    pontos_nivel_atual = (nivel_atual - 1) * 50
    pontos_proximo_nivel = nivel_atual * 50
    
    # Avoid division by zero and values > 100%
    if pontos_proximo_nivel - pontos_nivel_atual > 0:
        progresso_percentual = min(((pontos_atuais - pontos_nivel_atual) / (pontos_proximo_nivel - pontos_nivel_atual)) * 100, 100)
    else:
        progresso_percentual = 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card" style="background: linear-gradient(135deg, {cor}, {cor}dd); color: white;">
            <h4>⭐ Level</h4>
            <h2 style="color: white; font-size: 2.5em;">{nivel_atual}</h2>
            <p style="color: rgba(255,255,255,0.8);">Progress: {int(progresso_percentual)}%</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <h4>🏆 Points</h4>
            <h2 style="color: {cor};">{pontos_atuais}</h2>
            <p>+{pontos_proximo_nivel - pontos_atuais} to next</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <h4>🎖️ Achievements</h4>
            <h2 style="color: {cor};">{len(gami['conquistas'])}</h2>
            <p>Unlocked</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <h4>🔥 Actions</h4>
            <h2 style="color: {cor};">{gami['perguntas_professor'] + gami['questoes_revisadas']}</h2>
            <p>Performed</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Progress bar
    st.progress(progresso_percentual / 100, text=f"Level {nivel_atual} → {nivel_atual + 1}")
    
    # Show unlocked achievements
    if gami['conquistas']:
        st.markdown("### 🎖️ Your Achievements")
        cols = st.columns(3)
        for idx, conquista in enumerate(gami['conquistas']):
            with cols[idx % 3]:
                st.markdown(f'''
                <div class="main-card" style="text-align: center; border-left: 5px solid {cor};">
                    <h2 style="font-size: 2.5em; margin: 10px 0;">{conquista.get('emoji', '🏆')}</h2>
                    <h4 style="margin: 5px 0; color: {cor};">{conquista.get('nome', 'Achievement')}</h4>
                    <p style="font-size: 0.9em; color: #666;">{conquista.get('descricao', '')}</p>
                </div>
                ''', unsafe_allow_html=True)