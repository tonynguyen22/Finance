"""
        with col10:      
            # Transpose the income data so that the years are the columns
            income_statement_data = income_data.T

            # Display a markdown header for the income statement
            st.markdown('**Income Statement**')
                        
            # Allow the user to select a year to display
            year = st.selectbox('All numbers in thousands', income_statement_data.columns, label_visibility='collapsed')

            # Slice the income data to only show the selected year and format numbers with millify function
            income_statement_data = income_statement_data.loc[:, [year]]
            income_statement_data = income_statement_data.applymap(lambda x: millify(x, precision=2))
                        
            # Apply the color_highlighter function to highlight negative numbers
            income_statement_data = income_statement_data.style.applymap(color_highlighter)

            # Style the table headers with black color
            headers = {
                'selector': 'th:not(.index_name)',
                'props': [('color', 'black')]
            }

            income_statement_data.set_table_styles([headers])

            # Display the income statement table in Streamlit
            st.table(income_statement_data)
        """