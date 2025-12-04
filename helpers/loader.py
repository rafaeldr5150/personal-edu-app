# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def load_data(pd, st):
    """Loads student data"""
    try:
        df = pd.read_csv('/Users/mac/IronHacks/W9/Final Project 4/data/desempenho_alunos_questoes.csv')
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return False