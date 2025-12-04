# =============================================================================
# GRAPH AND VISUALIZATION FUNCTIONS
# =============================================================================

def criar_grafico_velocimetro(acertos, disciplina, cor, go):
    """Creates gauge chart to show correct answers from 0-18"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = acertos,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"{disciplina}", 'font': {'size': 24}},
        delta = {'reference': 9, 'increasing': {'color': cor}},
        gauge = {
            'axis': {'range': [None, 18], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': cor},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 6], 'color': 'lightcoral'},
                {'range': [6, 12], 'color': 'yellow'},
                {'range': [12, 18], 'color': 'lightgreen'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 14}}))
    
    fig.update_layout(
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def criar_grafico_conteudos_prioritarios(erros_port_df, erros_mat_df, px, pd):
    """Creates bar chart of contents with most errors"""
    conteudos_erros = []
    
    if not erros_port_df.empty:
        port_erros = erros_port_df['Conteúdo'].value_counts()
        for conteudo, erros in port_erros.items():
            conteudos_erros.append({'Conteúdo': conteudo, 'Erros': erros, 'Disciplina': 'Portuguese'})
    
    if not erros_mat_df.empty:
        mat_erros = erros_mat_df['Conteúdo'].value_counts()
        for conteudo, erros in mat_erros.items():
            conteudos_erros.append({'Conteúdo': conteudo, 'Erros': erros, 'Disciplina': 'Mathematics'})
    
    if not conteudos_erros:
        return None
    
    df_erros = pd.DataFrame(conteudos_erros)
    
    fig = px.bar(
        df_erros, 
        x='Conteúdo', 
        y='Erros', 
        color='Disciplina',
        color_discrete_map={'Portuguese': '#10b981', 'Mathematics': '#3b82f6'},
        title="Contents with Most Errors"
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    
    return fig