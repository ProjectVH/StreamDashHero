mkdir -p ~/.streamlit/
echo "
[general]n
email = "projectvaluehub@outlook.com"n
" > ~/.streamlit/credentials.toml
echo "
[server]n
headless = truen
enableCORS=falsen
port = $PORTn
" > ~/.streamlit/config.toml