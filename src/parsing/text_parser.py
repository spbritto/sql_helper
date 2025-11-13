"""
Parser de texto para extração de estrutura de banco de dados
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger


class TextParser:
    """Parser de documentos texto para estrutura de BD"""
    
    def __init__(self):
        # Padrões principais
        self.table_pattern = re.compile(
            r'(?:tabela|table):\s*(\w+)',
            re.IGNORECASE
        )
        self.field_pattern = re.compile(
            r'(?:campos|fields|colunas|columns):\s*(.+)',
            re.IGNORECASE
        )
        self.relationship_pattern = re.compile(
            r'fk\s*->\s*(\w+)',
            re.IGNORECASE
        )
        
        # Padrões alternativos para SQL DDL
        self.create_table_pattern = re.compile(
            r'CREATE\s+TABLE\s+(\w+)\s*\(',
            re.IGNORECASE
        )
        
        # Padrões para formato Markdown
        self.markdown_table_pattern = re.compile(
            r'#+\s*(?:tabela|table):\s*(\w+)',
            re.IGNORECASE
        )
    
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Faz parse do conteúdo texto e extrai estrutura do BD
        
        Args:
            content: Conteúdo do documento texto
            
        Returns:
            Dict com tables, relationships e metadata
        """
        try:
            logger.info("Iniciando parse de texto")
            
            # Detecta formato do conteúdo
            format_type = self._detect_format(content)
            logger.info(f"Formato detectado: {format_type}")
            
            # Extrai dados usando estratégia apropriada
            tables = self._extract_tables_smart(content, format_type)
            relationships = self._extract_relationships(content)
            
            # Detecta relacionamentos implícitos baseados nos campos
            implicit_relationships = self._detect_implicit_relationships(tables)
            relationships.extend(implicit_relationships)
            
            metadata = self._extract_metadata(content)
            metadata["detected_format"] = format_type
            
            # Validação
            tables = self._validate_and_clean_tables(tables)
            
            result = {
                "tables": tables,
                "relationships": relationships,
                "metadata": metadata
            }
            
            logger.success(f"Parse concluído: {len(tables)} tabelas encontradas")
            
            # Log detalhado por tabela
            for table in tables:
                logger.debug(f"Tabela '{table['name']}': {len(table.get('fields', []))} campos")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse: {e}")
            raise
    
    def _detect_format(self, content: str) -> str:
        """
        Detecta o formato do conteúdo
        
        Args:
            content: Conteúdo texto
            
        Returns:
            Tipo de formato: 'key_value', 'sql_ddl', 'markdown', 'unknown'
        """
        # Remove linhas vazias e espaços
        cleaned = content.strip()
        
        # Verifica SQL DDL
        if self.create_table_pattern.search(cleaned):
            return "sql_ddl"
        
        # Verifica Markdown
        if self.markdown_table_pattern.search(cleaned):
            return "markdown"
        
        # Verifica formato chave:valor
        if self.table_pattern.search(cleaned) and self.field_pattern.search(cleaned):
            return "key_value"
        
        return "unknown"
    
    def _extract_tables_smart(self, content: str, format_type: str) -> List[Dict[str, Any]]:
        """
        Extrai tabelas usando estratégia baseada no formato
        
        Args:
            content: Conteúdo texto
            format_type: Tipo de formato detectado
            
        Returns:
            Lista de tabelas extraídas
        """
        if format_type == "key_value":
            return self._extract_tables_key_value(content)
        elif format_type == "sql_ddl":
            return self._extract_tables_sql(content)
        elif format_type == "markdown":
            return self._extract_tables_markdown(content)
        else:
            # Fallback: tenta múltiplas estratégias
            logger.warning("Formato desconhecido, tentando múltiplas estratégias")
            tables = self._extract_tables_key_value(content)
            if not tables:
                tables = self._extract_tables_sql(content)
            if not tables:
                tables = self._extract_tables_markdown(content)
            return tables
    
    def _validate_and_clean_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Valida e limpa lista de tabelas
        
        Args:
            tables: Lista de tabelas
            
        Returns:
            Lista de tabelas validadas
        """
        validated = []
        
        for table in tables:
            # Verifica se tem nome
            if not table.get("name"):
                logger.warning(f"Tabela sem nome encontrada, ignorando: {table}")
                continue
            
            # Verifica se tem campos
            fields = table.get("fields", [])
            if not fields:
                logger.warning(f"Tabela '{table['name']}' não tem campos definidos")
            else:
                logger.info(f"✓ Tabela '{table['name']}': {len(fields)} campos carregados")
            
            validated.append(table)
        
        return validated
    
    def _extract_tables_key_value(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrai informações de tabelas no formato chave:valor
        Método melhorado com parsing por blocos
        
        Args:
            content: Conteúdo texto
            
        Returns:
            Lista de tabelas com seus campos
        """
        tables = []
        
        # Divide conteúdo em blocos por tabela
        # Procura todas as ocorrências de "tabela:"
        table_matches = list(self.table_pattern.finditer(content))
        
        if not table_matches:
            logger.warning("Nenhuma tabela encontrada com padrão 'tabela:'")
            return tables
        
        for i, table_match in enumerate(table_matches):
            table_name = table_match.group(1)
            table_start = table_match.start()
            
            # Define onde o bloco da tabela termina
            if i < len(table_matches) - 1:
                # Próxima tabela
                table_end = table_matches[i + 1].start()
            else:
                # Última tabela - pega até seção de relacionamentos ou fim
                rel_section = content.find("relacionamentos:", table_start)
                table_end = rel_section if rel_section != -1 else len(content)
            
            # Extrai bloco da tabela
            table_block = content[table_start:table_end]
            
            # Procura por campos dentro deste bloco
            fields = []
            field_match = self.field_pattern.search(table_block)
            
            if field_match:
                fields_str = field_match.group(1)
                fields = self._parse_fields(fields_str)
                logger.debug(f"Tabela '{table_name}': encontrados {len(fields)} campos")
            else:
                logger.warning(f"Tabela '{table_name}': nenhum campo encontrado no bloco")
            
            table = {
                "name": table_name,
                "fields": fields
            }
            
            tables.append(table)
        
        return tables
    
    def _extract_tables_sql(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrai tabelas de SQL DDL (CREATE TABLE)
        
        Args:
            content: Conteúdo SQL
            
        Returns:
            Lista de tabelas extraídas
        """
        tables = []
        
        # Procura por CREATE TABLE statements
        create_matches = self.create_table_pattern.finditer(content)
        
        for match in create_matches:
            table_name = match.group(1)
            
            # Tenta encontrar o fechamento do CREATE TABLE
            start_pos = match.end()
            paren_count = 1
            end_pos = start_pos
            
            for i in range(start_pos, len(content)):
                if content[i] == '(':
                    paren_count += 1
                elif content[i] == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        end_pos = i
                        break
            
            # Extrai definição dos campos
            fields_block = content[start_pos:end_pos]
            fields = self._parse_sql_fields(fields_block)
            
            tables.append({
                "name": table_name,
                "fields": fields
            })
        
        return tables
    
    def _extract_tables_markdown(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrai tabelas de formato Markdown
        
        Args:
            content: Conteúdo Markdown
            
        Returns:
            Lista de tabelas extraídas
        """
        tables = []
        
        # Procura por headers markdown com tabela
        markdown_matches = list(self.markdown_table_pattern.finditer(content))
        
        for i, match in enumerate(markdown_matches):
            table_name = match.group(1)
            start_pos = match.end()
            
            # Define fim do bloco
            if i < len(markdown_matches) - 1:
                end_pos = markdown_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            table_block = content[start_pos:end_pos]
            
            # Procura por campos
            fields = []
            field_match = self.field_pattern.search(table_block)
            if field_match:
                fields = self._parse_fields(field_match.group(1))
            
            tables.append({
                "name": table_name,
                "fields": fields
            })
        
        return tables
    
    def _parse_sql_fields(self, sql_block: str) -> List[Dict[str, Any]]:
        """
        Parse de campos de SQL DDL
        
        Args:
            sql_block: Bloco SQL com definição de campos
            
        Returns:
            Lista de campos parseados
        """
        fields = []
        
        # Divide por vírgula e processa cada linha
        lines = sql_block.split(',')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Padrão básico: nome tipo [constraints]
            parts = line.split()
            if len(parts) >= 2:
                field_name = parts[0].strip('`"[]')
                field_type = parts[1].upper()
                
                # Verifica constraints
                line_upper = line.upper()
                is_primary_key = 'PRIMARY KEY' in line_upper
                is_foreign_key = 'FOREIGN KEY' in line_upper or 'REFERENCES' in line_upper
                is_nullable = 'NOT NULL' not in line_upper
                
                fields.append({
                    "name": field_name,
                    "type": field_type,
                    "primary_key": is_primary_key,
                    "foreign_key": is_foreign_key,
                    "nullable": is_nullable,
                    "reference": None
                })
        
        return fields
    
    def _parse_fields(self, fields_str: str) -> List[Dict[str, Any]]:
        """
        Faz parse dos campos de uma tabela
        Suporta formatos Oracle complexos como NUMBER(5,0), VARCHAR2(10 BYTE)
        
        Args:
            fields_str: String com campos (ex: "COD VARCHAR2(5 BYTE), ANO (NUMBER(5,0))")
            
        Returns:
            Lista de campos parseados
        """
        fields = []
        
        # Remove espaços extras e normaliza
        fields_str = fields_str.strip()
        
        # Split inteligente por vírgula, respeitando parênteses
        field_parts = self._smart_split_fields(fields_str)
        
        for part in field_parts:
            part = part.strip()
            if not part:
                continue
            
            # Parse do campo
            parsed_field = self._parse_single_field(part)
            if parsed_field:
                fields.append(parsed_field)
        
        return fields
    
    def _smart_split_fields(self, fields_str: str) -> List[str]:
        """
        Divide string de campos por vírgula, respeitando parênteses aninhados
        
        Args:
            fields_str: String com campos
            
        Returns:
            Lista de strings, uma por campo
        """
        fields = []
        current_field = []
        paren_depth = 0
        
        for char in fields_str:
            if char == '(':
                paren_depth += 1
                current_field.append(char)
            elif char == ')':
                paren_depth -= 1
                current_field.append(char)
            elif char == ',' and paren_depth == 0:
                # Vírgula fora de parênteses - é separador de campos
                fields.append(''.join(current_field).strip())
                current_field = []
            else:
                current_field.append(char)
        
        # Adiciona último campo
        if current_field:
            fields.append(''.join(current_field).strip())
        
        return fields
    
    def _parse_single_field(self, field_str: str) -> Optional[Dict[str, Any]]:
        """
        Faz parse de um único campo
        Suporta formatos:
        - NOME_CAMPO	TIPO (Oracle com TAB)
        - NOME_CAMPO (TIPO)
        - NOME_CAMPO (TIPO(params))
        
        Args:
            field_str: String de um campo
            
        Returns:
            Dict com informações do campo ou None
        """
        # Padrão 1: NOME (TIPO_COMPLETO) ou NOME (TIPO(params))
        # Usa regex que captura tudo entre parênteses balanceados
        match_with_parens = re.match(r'(\w+)\s*\((.+)\)\s*$', field_str)
        
        if match_with_parens:
            field_name = match_with_parens.group(1)
            field_type_raw = match_with_parens.group(2).strip()
            
            # Limpa e normaliza o tipo
            field_type = self._normalize_field_type(field_type_raw)
            
            # Verifica se tem indicadores de PK/FK no tipo
            type_lower = field_type_raw.lower()
            is_primary_key = 'pk' in type_lower or 'primary key' in type_lower
            is_foreign_key = 'fk' in type_lower or 'foreign key' in type_lower
            is_nullable = 'null' in type_lower and 'not null' not in type_lower
            
            # Extrai referência de FK se houver
            fk_reference = None
            fk_match = self.relationship_pattern.search(field_type_raw)
            if fk_match:
                fk_reference = fk_match.group(1)
            
            return {
                "name": field_name,
                "type": field_type,
                "primary_key": is_primary_key,
                "foreign_key": is_foreign_key,
                "nullable": is_nullable if is_nullable or is_primary_key or is_foreign_key else True,
                "reference": fk_reference
            }
        
        # Padrão 2: NOME_CAMPO	TIPO (separado por TAB ou espaços)
        # Usado no primeiro campo de tabelas Oracle
        parts = re.split(r'\s+', field_str, maxsplit=1)
        
        if len(parts) == 2:
            field_name = parts[0].strip()
            field_type_raw = parts[1].strip()
            field_type = self._normalize_field_type(field_type_raw)
            
            return {
                "name": field_name,
                "type": field_type,
                "primary_key": False,
                "foreign_key": False,
                "nullable": True,
                "reference": None
            }
        
        # Padrão 3: Apenas nome (sem tipo)
        if len(parts) == 1:
            return {
                "name": field_str.strip(),
                "type": "unknown",
                "primary_key": False,
                "foreign_key": False,
                "nullable": True,
                "reference": None
            }
        
        return None
    
    def _normalize_field_type(self, type_str: str) -> str:
        """
        Normaliza tipo de campo, removendo metadados desnecessários
        
        Args:
            type_str: String do tipo (ex: "VARCHAR2(10 BYTE)" ou "NUMBER(5,0)")
            
        Returns:
            Tipo normalizado
        """
        # Remove indicadores de PK/FK/etc que não fazem parte do tipo
        type_str = type_str.strip()
        
        # Remove palavras-chave que não são parte do tipo SQL
        keywords_to_remove = ['pk', 'primary key', 'fk', 'foreign key', 'nullable', 'not null']
        type_lower = type_str.lower()
        
        for keyword in keywords_to_remove:
            if keyword in type_lower and not type_str.upper().startswith(('VARCHAR', 'CHAR', 'NUMBER', 'DATE', 'INT')):
                # Remove apenas se não for parte do tipo SQL
                type_str = re.sub(r'\b' + re.escape(keyword) + r'\b', '', type_str, flags=re.IGNORECASE)
        
        # Limpa espaços extras
        type_str = ' '.join(type_str.split())
        
        return type_str if type_str else "unknown"
    
    def _extract_relationships(self, content: str) -> List[Dict[str, str]]:
        """
        Extrai relacionamentos entre tabelas (explícitos)
        
        Formatos suportados:
        1. tabela1.campo1 -> tabela2.campo2
        2. Seção "relacionamentos:" com lista de relacionamentos
        
        Args:
            content: Conteúdo texto
            
        Returns:
            Lista de relacionamentos
        """
        relationships = []
        
        # 1. Procura por padrões de relacionamento inline
        # Exemplo: "pedidos.usuario_id -> usuarios.id"
        rel_pattern = re.compile(
            r'(\w+)\.(\w+)\s*->\s*(\w+)\.(\w+)',
            re.IGNORECASE
        )
        
        for match in rel_pattern.finditer(content):
            relationship = {
                "from_table": match.group(1),
                "from_field": match.group(2),
                "to_table": match.group(3),
                "to_field": match.group(4),
                "type": "foreign_key",
                "detected": "explicit"
            }
            relationships.append(relationship)
        
        # 2. Procura por seção dedicada de relacionamentos
        # Formato:
        # relacionamentos:
        # tabela1.campo1 -> tabela2.campo2
        # tabela1.campo2 -> tabela3.campo1
        rel_section_pattern = re.compile(
            r'(?:relacionamentos|relationships):\s*\n((?:.*\n)*?)(?=\n\s*\n|\n\s*(?:tabela|table):|$)',
            re.IGNORECASE | re.MULTILINE
        )
        
        rel_section_match = rel_section_pattern.search(content)
        if rel_section_match:
            rel_section = rel_section_match.group(1)
            logger.debug(f"Seção de relacionamentos encontrada: {len(rel_section)} caracteres")
            
            # Parse cada linha da seção
            for line in rel_section.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Tenta fazer match com padrão de relacionamento
                match = rel_pattern.search(line)
                if match:
                    # Verifica se já não foi adicionado
                    rel_key = f"{match.group(1)}.{match.group(2)}->{match.group(3)}.{match.group(4)}"
                    exists = any(
                        f"{r['from_table']}.{r['from_field']}->{r['to_table']}.{r['to_field']}" == rel_key
                        for r in relationships
                    )
                    
                    if not exists:
                        relationship = {
                            "from_table": match.group(1),
                            "from_field": match.group(2),
                            "to_table": match.group(3),
                            "to_field": match.group(4),
                            "type": "foreign_key",
                            "detected": "explicit"
                        }
                        relationships.append(relationship)
        
        logger.debug(f"Relacionamentos explícitos encontrados: {len(relationships)}")
        
        return relationships
    
    def _detect_implicit_relationships(self, tables: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Detecta relacionamentos implícitos entre tabelas analisando campos
        
        Heurísticas usadas:
        - Campos com nomes similares em diferentes tabelas
        - Campos com prefixos comuns (COD_, NUM_, ID_)
        - Campos com tipos compatíveis
        
        Args:
            tables: Lista de tabelas com seus campos
            
        Returns:
            Lista de relacionamentos detectados
        """
        relationships = []
        
        if len(tables) < 2:
            logger.debug("Menos de 2 tabelas, não há relacionamentos implícitos")
            return relationships
        
        logger.info("Detectando relacionamentos implícitos...")
        
        # Analisa cada par de tabelas
        for i, table1 in enumerate(tables):
            for table2 in tables[i + 1:]:
                table1_name = table1.get("name", "")
                table2_name = table2.get("name", "")
                
                table1_fields = table1.get("fields", [])
                table2_fields = table2.get("fields", [])
                
                # Compara campos entre as tabelas
                for field1 in table1_fields:
                    field1_name = field1.get("name", "")
                    field1_type = field1.get("type", "")
                    
                    for field2 in table2_fields:
                        field2_name = field2.get("name", "")
                        field2_type = field2.get("type", "")
                        
                        # Verifica se há similaridade entre campos
                        similarity_score = self._calculate_field_similarity(
                            field1_name, field2_name, field1_type, field2_type
                        )
                        
                        if similarity_score >= 0.7:  # Threshold de similaridade
                            # Detectou relacionamento provável
                            relationship = {
                                "from_table": table1_name,
                                "from_field": field1_name,
                                "to_table": table2_name,
                                "to_field": field2_name,
                                "type": "possible_foreign_key",
                                "detected": "implicit",
                                "confidence": round(similarity_score, 2)
                            }
                            relationships.append(relationship)
                            
                            logger.debug(
                                f"Relacionamento detectado: {table1_name}.{field1_name} <-> "
                                f"{table2_name}.{field2_name} (confiança: {similarity_score:.2f})"
                            )
        
        logger.success(f"Relacionamentos implícitos detectados: {len(relationships)}")
        return relationships
    
    def _calculate_field_similarity(
        self, 
        name1: str, 
        name2: str, 
        type1: str, 
        type2: str
    ) -> float:
        """
        Calcula similaridade entre dois campos
        
        Args:
            name1: Nome do campo 1
            name2: Nome do campo 2
            type1: Tipo do campo 1
            type2: Tipo do campo 2
            
        Returns:
            Score de similaridade (0.0 a 1.0)
        """
        score = 0.0
        
        # Normaliza nomes
        name1_clean = self._normalize_field_name(name1)
        name2_clean = self._normalize_field_name(name2)
        
        # 1. Verifica nomes idênticos (score máximo)
        if name1_clean == name2_clean:
            score = 1.0
        else:
            # 2. Verifica se um nome contém o outro
            if name1_clean in name2_clean or name2_clean in name1_clean:
                score = 0.8
            
            # 3. Verifica prefixos/sufixos comuns
            elif self._has_common_prefix(name1_clean, name2_clean):
                score = 0.75
            
            # 4. Verifica se compartilham palavras-chave
            elif self._shares_keywords(name1_clean, name2_clean):
                score = 0.7
        
        # Ajusta score baseado em compatibilidade de tipos
        if score > 0 and not self._are_types_compatible(type1, type2):
            score *= 0.5  # Reduz score se tipos são incompatíveis
        
        return score
    
    def _normalize_field_name(self, name: str) -> str:
        """
        Normaliza nome de campo removendo prefixos/sufixos comuns
        
        Args:
            name: Nome do campo
            
        Returns:
            Nome normalizado
        """
        name = name.upper().strip()
        
        # Remove underscores múltiplos
        name = re.sub(r'_+', '_', name)
        
        # Remove prefixos muito comuns que não agregam ao significado
        # Mas mantém prefixos importantes como COD_, NUM_, ID_
        
        return name
    
    def _has_common_prefix(self, name1: str, name2: str) -> bool:
        """
        Verifica se dois nomes compartilham prefixo significativo
        
        Args:
            name1: Nome 1
            name2: Nome 2
            
        Returns:
            True se compartilham prefixo
        """
        # Prefixos significativos comuns em bancos Oracle/SQL
        prefixes = ['COD_', 'NUM_', 'ID_', 'IND_', 'DAT_', 'SGL_', 'DSC_', 'VLR_', 'QTD_', 'ANO_', 'MES_']
        
        for prefix in prefixes:
            if name1.startswith(prefix) and name2.startswith(prefix):
                # Ambos têm o mesmo prefixo, verifica se resto é similar
                suffix1 = name1[len(prefix):]
                suffix2 = name2[len(prefix):]
                
                # Checa se sufixos são similares (ao menos 50% de overlap)
                if suffix1 in suffix2 or suffix2 in suffix1:
                    return True
                
                # Checa abreviações comuns
                if self._are_abbreviations(suffix1, suffix2):
                    return True
        
        return False
    
    def _shares_keywords(self, name1: str, name2: str) -> bool:
        """
        Verifica se dois nomes compartilham palavras-chave significativas
        
        Args:
            name1: Nome 1
            name2: Nome 2
            
        Returns:
            True se compartilham keywords
        """
        # Divide por underscore
        words1 = set(name1.split('_'))
        words2 = set(name2.split('_'))
        
        # Remove palavras muito comuns que não são significativas
        common_words = {'DE', 'DO', 'DA', 'EM', 'A', 'O', 'E', 'PARA', 'COM'}
        words1 = words1 - common_words
        words2 = words2 - common_words
        
        # Verifica interseção
        intersection = words1 & words2
        
        # Se compartilham ao menos 2 palavras ou 50% das palavras
        if len(intersection) >= 2:
            return True
        
        if len(words1) > 0 and len(words2) > 0:
            overlap = len(intersection) / min(len(words1), len(words2))
            return overlap >= 0.5
        
        return False
    
    def _are_abbreviations(self, name1: str, name2: str) -> bool:
        """
        Verifica se dois nomes são abreviações um do outro
        
        Args:
            name1: Nome 1
            name2: Nome 2
            
        Returns:
            True se são abreviações
        """
        # Mapeamento de abreviações comuns
        abbreviations = {
            'LCT': 'LANCAMENTO',
            'CTZ': 'CONTABILIZACAO',
            'FLC': 'FLC',  # Já é abreviação
            'FOL': 'FOLHA',
            'LIN': 'LINHA',
            'ORG': 'ORIGEM',
            'CTB': 'CONTABIL',
            'CNTBL': 'CONTABIL',
            'LACTO': 'LANCAMENTO'
        }
        
        # Tenta expandir abreviações e comparar
        expanded1 = abbreviations.get(name1, name1)
        expanded2 = abbreviations.get(name2, name2)
        
        return expanded1 == expanded2 or expanded1 in expanded2 or expanded2 in expanded1
    
    def _are_types_compatible(self, type1: str, type2: str) -> bool:
        """
        Verifica se dois tipos de dados são compatíveis para relacionamento
        
        Args:
            type1: Tipo 1
            type2: Tipo 2
            
        Returns:
            True se compatíveis
        """
        # Normaliza tipos
        type1_base = self._get_base_type(type1.upper())
        type2_base = self._get_base_type(type2.upper())
        
        # Tipos idênticos são compatíveis
        if type1_base == type2_base:
            return True
        
        # Grupos de tipos compatíveis
        numeric_types = {'NUMBER', 'INTEGER', 'INT', 'DECIMAL', 'NUMERIC', 'FLOAT'}
        string_types = {'VARCHAR', 'VARCHAR2', 'CHAR', 'TEXT', 'STRING'}
        date_types = {'DATE', 'DATETIME', 'TIMESTAMP'}
        
        # Verifica se ambos estão no mesmo grupo
        if type1_base in numeric_types and type2_base in numeric_types:
            return True
        if type1_base in string_types and type2_base in string_types:
            return True
        if type1_base in date_types and type2_base in date_types:
            return True
        
        return False
    
    def _get_base_type(self, type_str: str) -> str:
        """
        Extrai tipo base de uma string de tipo (remove parâmetros)
        
        Args:
            type_str: String do tipo (ex: "NUMBER(5,0)")
            
        Returns:
            Tipo base (ex: "NUMBER")
        """
        # Remove tudo após parênteses
        match = re.match(r'^(\w+)', type_str)
        if match:
            return match.group(1).upper()
        return type_str.upper()
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extrai metadados adicionais
        
        Args:
            content: Conteúdo texto
            
        Returns:
            Dict com metadados
        """
        metadata = {
            "source": "text",
            "line_count": len(content.split('\n')),
            "char_count": len(content)
        }
        
        # Tenta extrair nome do banco
        db_pattern = re.compile(
            r'(?:banco|database|db):\s*(\w+)',
            re.IGNORECASE
        )
        db_match = db_pattern.search(content)
        if db_match:
            metadata["database_name"] = db_match.group(1)
        
        return metadata

