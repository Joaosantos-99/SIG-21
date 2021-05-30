# SIG-21

Neste trabalho procedeu-se ao desenvolvimento de um plugin para o software QGIS, capaz de representar num mapa os Monumentos Nacionais e/ou Museus de Portugal.

Quando o plugin é executado, aparece uma janela onde o utilizador tem opção de escolher o que pretende visualizar no mapa: Museus, Monumentos ou ambos.
Desta forma, consoante o escolhido, surge um mapa mundo, com ícones correspondentes aos museus e monumentos portugueses no seu local de coordenadas. 

Focando nos Monumentos, ao clicar num ícone surgem informações sobre o monumento em questão, mais especificamente o seu nome, localização, um weblink para uma foto do monumento, o seu id de Património Cultural e um weblink para informações sobre o mesmo.
No que toca aos museus, é apresentado o seu nome, localidade, um weblink para uma foto do museu e outro para informações sobre o mesmo e, por fim, a data da sua criação, quando existente.

Procedimento:
1) Desenvolvimento de uma query no wikidata, de forma a obter informação sobre os mesmo temas.
2) Implementação de uma script em Python para garantir a busca de informação e o tratamento dos dados.
3) Após o correto funcionamento da script, utilizou-se o Plugin Builder, por forma a facilitar a implementação deste plugin e assim garantir maior facilidade na sua utilização.
4) Para alterar o display da janela apresentada no momento inicial utilizou-se a aplicação QTCreator. 
