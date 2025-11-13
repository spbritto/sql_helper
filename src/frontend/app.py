"""
Interface Streamlit para o Assistente SQL
"""
import streamlit as st
import requests
from typing import Optional
import os
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Assistente SQL",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da API (pode ser configurada via variável de ambiente)
API_URL = os.getenv("API_URL", "http://localhost:8000")


def init_session_state():
    """Inicializa o estado da sessão"""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_structure' not in st.session_state:
        st.session_state.current_structure = None


def upload_structure_page():
    """Página de upload de estrutura"""
    st.header("📊 Carregar Estrutura do Banco de Dados")
    
    tab1, tab2 = st.tabs(["📝 Texto", "🖼️ Imagem"])
    
    with tab1:
        st.subheader("Upload de arquivo texto")
        st.markdown("""
        **Formato esperado:**
        ```
        tabela: usuarios
        campos: id (int, pk), nome (varchar), email (varchar), data_cadastro (datetime)
        
        tabela: pedidos
        campos: id (int, pk), usuario_id (int, fk->usuarios), valor (decimal), status (varchar)
        ```
        """)
        
        text_file = st.file_uploader(
            "Escolha um arquivo .txt",
            type=['txt', 'sql', 'ddl'],
            key='text_upload'
        )
        
        if text_file:
            if st.button("Processar Arquivo Texto"):
                with st.spinner("Processando..."):
                    try:
                        files = {'file': text_file}
                        response = requests.post(
                            f"{API_URL}/api/structure/upload-text",
                            files=files
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ Estrutura extraída com sucesso!")
                            st.json(result['structure'])
                            st.session_state.current_structure = result['structure']
                        else:
                            st.error(f"❌ Erro: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Erro ao processar: {str(e)}")
    
    with tab2:
        st.subheader("Upload de imagem (OCR)")
        st.info("📸 Faça upload de prints de diagramas ER, DDL, ou estruturas de banco")
        
        image_file = st.file_uploader(
            "Escolha uma imagem",
            type=['png', 'jpg', 'jpeg', 'bmp'],
            key='image_upload'
        )
        
        if image_file:
            st.image(image_file, caption="Imagem carregada", use_column_width=True)
            
            if st.button("Processar Imagem (OCR)"):
                with st.spinner("Processando OCR..."):
                    try:
                        files = {'file': image_file}
                        response = requests.post(
                            f"{API_URL}/api/structure/upload-image",
                            files=files
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ Estrutura extraída via OCR!")
                            st.json(result['structure'])
                            st.session_state.current_structure = result['structure']
                        else:
                            st.error(f"❌ Erro: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Erro ao processar: {str(e)}")


def query_generator_page():
    """Página de geração de queries"""
    st.header("💬 Gerador de Queries SQL")
    
    # Status da estrutura
    if st.session_state.current_structure:
        st.success("✅ Estrutura carregada")
    else:
        st.warning("⚠️ Nenhuma estrutura carregada. Carregue uma estrutura primeiro.")
    
    # Input de linguagem natural
    st.subheader("Faça sua pergunta")
    
    question = st.text_area(
        "Digite sua pergunta em linguagem natural:",
        placeholder="Ex: Quais são os 10 usuários com mais pedidos nos últimos 30 dias?",
        height=100
    )
    
    context = st.text_input(
        "Contexto adicional (opcional):",
        placeholder="Ex: Considere apenas pedidos com status 'concluído'"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        generate_button = st.button("🚀 Gerar Query", type="primary")
    
    if generate_button and question:
        with st.spinner("Gerando query SQL..."):
            try:
                payload = {
                    "question": question,
                    "context": context if context else None
                }
                
                response = requests.post(
                    f"{API_URL}/api/query/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Exibe a query gerada
                    st.subheader("📝 Query Gerada")
                    st.code(result['sql'], language='sql')
                    
                    # Explicação
                    st.subheader("💡 Explicação")
                    st.info(result['explanation'])
                    
                    # Confiança
                    confidence = result['confidence']
                    st.metric("Confiança", f"{confidence*100:.1f}%")
                    
                    # Otimizações
                    if result.get('optimizations'):
                        with st.expander("⚡ Sugestões de Otimização"):
                            for opt in result['optimizations']:
                                st.write(f"• {opt}")
                    
                    # Avisos
                    if result.get('warnings'):
                        with st.expander("⚠️ Avisos"):
                            for warn in result['warnings']:
                                st.warning(warn)
                    
                    # Adiciona ao histórico
                    st.session_state.history.append({
                        'question': question,
                        'sql': result['sql'],
                        'explanation': result['explanation']
                    })
                    
                else:
                    st.error(f"❌ Erro: {response.text}")
            except Exception as e:
                st.error(f"❌ Erro ao gerar query: {str(e)}")
                st.info("💡 Certifique-se de que a API está rodando em http://localhost:8000")


def structure_viewer_page():
    """Página de visualização da estrutura carregada"""
    st.header("📊 Visualizar Estrutura Carregada")
    
    try:
        # Busca estrutura atual da API
        response = requests.get(f"{API_URL}/api/structure/current", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            
            if not result.get("loaded"):
                st.warning("⚠️ Nenhuma estrutura carregada no momento")
                st.info("💡 Vá para 'Carregar Estrutura' para fazer upload de um arquivo")
                return
            
            structure = result.get("structure")
            summary = result.get("summary")
            
            # Informações gerais
            st.subheader("📋 Resumo da Estrutura")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Tabelas", summary.get("total_tables", 0))
            with col2:
                st.metric("Relacionamentos", summary.get("total_relationships", 0))
            with col3:
                st.metric("Formato", summary.get("format", "N/A").upper())
            with col4:
                created = summary.get("created_at", "N/A")
                if created != "N/A":
                    created = created.split("T")[0]  # Apenas data
                st.metric("Carregada em", created)
            
            st.markdown("---")
            
            # Botão para limpar estrutura
            col_clear1, col_clear2 = st.columns([1, 5])
            with col_clear1:
                if st.button("🗑️ Limpar Estrutura", type="secondary"):
                    try:
                        clear_response = requests.delete(f"{API_URL}/api/structure/current")
                        if clear_response.status_code == 200:
                            st.success("✅ Estrutura removida com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao remover estrutura")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            
            st.markdown("---")
            
            # Visualização por tabela
            st.subheader("📑 Tabelas e Campos")
            
            tables = structure.get("tables", [])
            
            if not tables:
                st.info("Nenhuma tabela encontrada na estrutura")
                return
            
            # Tabs para cada tabela
            table_names = [table.get("name", f"Tabela {i+1}") for i, table in enumerate(tables)]
            
            if len(tables) == 1:
                # Se só tiver uma tabela, não usa tabs
                table = tables[0]
                _render_table_details(table, structure)
            else:
                # Múltiplas tabelas - usa tabs
                tabs = st.tabs(table_names)
                
                for i, tab in enumerate(tabs):
                    with tab:
                        table = tables[i]
                        _render_table_details(table, structure)
            
            # Relacionamentos
            st.markdown("---")
            st.subheader("🔗 Relacionamentos Entre Tabelas")
            
            relationships = structure.get("relationships", [])
            
            if relationships:
                # Estatísticas de relacionamentos
                explicit_rels = [r for r in relationships if r.get('detected') == 'explicit']
                implicit_rels = [r for r in relationships if r.get('detected') == 'implicit']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total", len(relationships))
                with col2:
                    st.metric("Explícitos", len(explicit_rels), help="Definidos no arquivo")
                with col3:
                    st.metric("Detectados", len(implicit_rels), help="Detectados automaticamente")
                
                st.markdown("")
                
                # Opção de filtro
                filter_option = st.radio(
                    "Mostrar:",
                    ["Todos", "Apenas Explícitos", "Apenas Detectados"],
                    horizontal=True
                )
                
                # Filtra relacionamentos
                filtered_rels = relationships
                if filter_option == "Apenas Explícitos":
                    filtered_rels = explicit_rels
                elif filter_option == "Apenas Detectados":
                    filtered_rels = implicit_rels
                
                # Prepara dados para visualização
                rel_data = []
                for rel in filtered_rels:
                    detected = rel.get('detected', 'unknown')
                    confidence = rel.get('confidence', '')
                    
                    badge = "🔵" if detected == "explicit" else "🟡"
                    confidence_text = f"{confidence}" if confidence else "N/A"
                    
                    rel_data.append({
                        "": badge,
                        "De": f"{rel.get('from_table', 'N/A')}.{rel.get('from_field', 'N/A')}",
                        "Para": f"{rel.get('to_table', 'N/A')}.{rel.get('to_field', 'N/A')}",
                        "Tipo": rel.get('type', 'N/A'),
                        "Confiança": confidence_text
                    })
                
                st.dataframe(
                    rel_data, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "": st.column_config.TextColumn("", width="small"),
                        "De": st.column_config.TextColumn("De", width="large"),
                        "Para": st.column_config.TextColumn("Para", width="large"),
                        "Tipo": st.column_config.TextColumn("Tipo", width="medium"),
                        "Confiança": st.column_config.TextColumn("Confiança", width="small")
                    }
                )
                
                st.caption("🔵 Explícito  |  🟡 Detectado automaticamente")
            else:
                st.info("Nenhum relacionamento encontrado")
            
            # Metadados
            with st.expander("ℹ️ Metadados Adicionais"):
                metadata = structure.get("metadata", {})
                st.json(metadata)
        
        else:
            st.error(f"❌ Erro ao buscar estrutura: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Não foi possível conectar à API")
        st.info("💡 Certifique-se de que a API está rodando em http://localhost:8000")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")


def _render_table_details(table: dict, structure: dict = None):
    """
    Renderiza detalhes de uma tabela, incluindo relacionamentos
    
    Args:
        table: Dict com informações da tabela
        structure: Dict com estrutura completa (para buscar relacionamentos)
    """
    table_name = table.get("name", "N/A")
    fields = table.get("fields", [])
    
    st.markdown(f"### 📋 {table_name}")
    st.caption(f"Total de campos: {len(fields)}")
    
    if not fields:
        st.warning(f"⚠️ Tabela '{table_name}' não possui campos definidos")
        return
    
    # Busca relacionamentos desta tabela
    table_relationships = []
    if structure:
        relationships = structure.get("relationships", [])
        table_relationships = [
            r for r in relationships
            if r.get('from_table') == table_name or r.get('to_table') == table_name
        ]
    
    # Cria mapa de campos -> tabelas relacionadas
    field_relationships = {}
    for rel in table_relationships:
        if rel.get('from_table') == table_name:
            field_name = rel.get('from_field')
            other_table = rel.get('to_table')
            other_field = rel.get('to_field')
        else:
            field_name = rel.get('to_field')
            other_table = rel.get('from_table')
            other_field = rel.get('from_field')
        
        if field_name not in field_relationships:
            field_relationships[field_name] = []
        
        confidence = rel.get('confidence', '')
        confidence_str = f" ({confidence})" if confidence else ""
        field_relationships[field_name].append(f"{other_table}.{other_field}{confidence_str}")
    
    # Prepara dados para visualização
    field_data = []
    for field in fields:
        field_name = field.get("name", "N/A")
        
        # Pega relacionamentos deste campo
        related_fields = field_relationships.get(field_name, [])
        ref_text = field.get("reference", "") or ""
        
        # Adiciona relacionamentos detectados
        if related_fields:
            if ref_text:
                ref_text += " | "
            ref_text += ", ".join(related_fields[:2])  # Mostra até 2 relacionamentos
            if len(related_fields) > 2:
                ref_text += f" +{len(related_fields)-2}"
        
        field_data.append({
            "Campo": field_name,
            "Tipo": field.get("type", "N/A"),
            "PK": "✓" if field.get("primary_key", False) else "",
            "FK": "✓" if field.get("foreign_key", False) else "",
            "Relacionado com": ref_text,
            "Nullable": "✓" if field.get("nullable", True) else ""
        })
    
    # Exibe como tabela
    st.dataframe(
        field_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Campo": st.column_config.TextColumn("Campo", width="medium"),
            "Tipo": st.column_config.TextColumn("Tipo", width="medium"),
            "PK": st.column_config.TextColumn("PK", width="small"),
            "FK": st.column_config.TextColumn("FK", width="small"),
            "Relacionado com": st.column_config.TextColumn("Relacionado com", width="large"),
            "Nullable": st.column_config.TextColumn("Nullable", width="small")
        }
    )
    
    # Estatísticas da tabela
    pk_count = sum(1 for f in fields if f.get("primary_key", False))
    fk_count = sum(1 for f in fields if f.get("foreign_key", False))
    related_fields_count = len(field_relationships)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Campos", len(fields))
    with col2:
        st.metric("Chaves Primárias", pk_count)
    with col3:
        st.metric("Chaves Estrangeiras", fk_count)
    with col4:
        st.metric("Campos Relacionados", related_fields_count)
    
    # Mostra resumo de relacionamentos desta tabela
    if table_relationships:
        with st.expander(f"🔗 Relacionamentos de {table_name} ({len(table_relationships)})"):
            # Agrupa por tabela relacionada
            related_tables = {}
            for rel in table_relationships:
                if rel.get('from_table') == table_name:
                    other_table = rel.get('to_table')
                else:
                    other_table = rel.get('from_table')
                
                if other_table not in related_tables:
                    related_tables[other_table] = []
                related_tables[other_table].append(rel)
            
            # Mostra por tabela relacionada
            for other_table, rels in related_tables.items():
                st.markdown(f"**{other_table}** ({len(rels)} relacionamento(s))")
                for rel in rels[:5]:  # Mostra até 5
                    if rel.get('from_table') == table_name:
                        this_field = rel.get('from_field')
                        other_field = rel.get('to_field')
                    else:
                        this_field = rel.get('to_field')
                        other_field = rel.get('from_field')
                    
                    confidence = rel.get('confidence', '')
                    detected = rel.get('detected', '')
                    
                    badge = "🔵" if detected == "explicit" else "🟡"
                    confidence_text = f" (confiança: {confidence})" if confidence else ""
                    
                    st.caption(f"{badge} `{this_field}` ↔ `{other_field}`{confidence_text}")
                
                if len(rels) > 5:
                    st.caption(f"... e mais {len(rels)-5} relacionamento(s)")
                st.markdown("")


def history_page():
    """Página de histórico"""
    st.header("📜 Histórico de Queries")
    
    if not st.session_state.history:
        st.info("Nenhuma query gerada ainda.")
        return
    
    for idx, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Query {len(st.session_state.history) - idx}: {item['question'][:50]}..."):
            st.markdown(f"**Pergunta:** {item['question']}")
            st.code(item['sql'], language='sql')
            st.markdown(f"**Explicação:** {item['explanation']}")


def sidebar():
    """Sidebar com navegação"""
    with st.sidebar:
        st.title("🤖 Assistente SQL")
        st.markdown("---")
        
        page = st.radio(
            "Navegação",
            ["🏠 Início", "📊 Carregar Estrutura", "🔍 Visualizar Estrutura", "💬 Gerar Query", "📜 Histórico"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Status da API
        try:
            response = requests.get(f"{API_URL}/api/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ API Online")
            else:
                st.error("❌ API com problemas")
        except:
            st.error("❌ API Offline")
            st.caption("Inicie a API com: `python src/backend/main.py`")
        
        st.markdown("---")
        
        # Status da estrutura carregada
        try:
            structure_response = requests.get(f"{API_URL}/api/structure/current", timeout=2)
            if structure_response.status_code == 200:
                result = structure_response.json()
                if result.get("loaded"):
                    summary = result.get("summary", {})
                    st.info(f"📋 Estrutura carregada\n\n{summary.get('total_tables', 0)} tabelas")
                else:
                    st.warning("⚠️ Nenhuma estrutura carregada")
        except:
            pass
        
        st.markdown("---")
        st.caption("v1.0.0")
        
        return page


def main():
    """Função principal"""
    init_session_state()
    
    page = sidebar()
    
    if page == "🏠 Início":
        st.title("🤖 Assistente Inteligente de Queries SQL")
        st.markdown("""
        ## Bem-vindo!
        
        Este assistente ajuda você a gerar queries SQL otimizadas a partir de linguagem natural.
        
        ### 📋 Como usar:
        
        1. **Carregar Estrutura**: Faça upload da estrutura do seu banco de dados (texto ou imagem)
        2. **Visualizar Estrutura**: Veja detalhadamente as tabelas e campos carregados
        3. **Gerar Query**: Digite sua pergunta em linguagem natural
        4. **Revisar**: Veja a query gerada, explicação e sugestões de otimização
        5. **Histórico**: Acesse queries anteriores
        
        ### 🚀 Recursos:
        
        - ✅ Processamento de linguagem natural
        - ✅ OCR para extração de estruturas
        - ✅ **Visualização detalhada de estruturas** (NOVO!)
        - ✅ Suporte a múltiplos formatos de entrada
        - ✅ Otimização automática de queries
        - ✅ Explicações detalhadas
        - ✅ Histórico de queries
        
        ---
        
        👈 Use o menu lateral para começar!
        """)
        
    elif page == "📊 Carregar Estrutura":
        upload_structure_page()
        
    elif page == "🔍 Visualizar Estrutura":
        structure_viewer_page()
        
    elif page == "💬 Gerar Query":
        query_generator_page()
        
    elif page == "📜 Histórico":
        history_page()


if __name__ == "__main__":
    main()

