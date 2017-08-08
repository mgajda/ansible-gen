scp -r dockerProject targetHost:
ssh targetHost <<ENDREMOTE
cd dockerProject
sudo docker build -f Dockerfile-cpu -t ihaskell-nlp:latest .
sudo docker run -p 8888:8888 ihaskell-nlp:latest
ENDREMOTE
