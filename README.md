# Q-learning

Aplicatia reprezinta implementarea algoritmului de invatare prin recompensa Q-learning pentru jocul de Pong. 
Jocul se realizeaza intre 2 jucatori: agentul (stanga) si adversarul (dreapta). Adversarul functioneaza dupa niste euristici predefinite (vezi enunt), iar agentul foloseste algoritmul Q-learning pentru a determina urmatoarea mutare. O stare este reprezentata de un tuplu (pozitia agentului, pozitia adversarului, pozitia mingii si directia mingii). Actiunile sunt: deplasare in sus cu o casuta, deplasare in jos sau stat pe loc. Recompensele sunt: 1 pentru castig, -1 pentru pierdere si 0 pentru celelalte stari. Algoritmul pastreaza un dictionar cu elemente de tipul (stare, actiune) in care memoreaza pentru fiecare pereche o utilitate estimata, care se actualizeaza pe masura ce agentul se antreneaza. Agentul epsilon-greedy, la fiecare pas, cu o probabilitate epsilon, selecteaza o actiune aleatoare, iar in rest selecteaza actiunea cu cea mai mare utilitate din starea curenta. 
Aplicatia contine doua etape mari: o etapa de antrenare si o etapa de testare. 
Aplicatia se poate rula din terminal astfel: 
$ python pong.py --learning_rate 0.1 --epsilon 0.05 --train_episodes 1000 --eval_episodes 10 --max_frames 30 --agent_strategy 2 --opponent_strategy 0 --sleep 0.0
Parametrii au urmatoarea semnificatie: 
- train_episodes - numarul de episoare de antrenare
- eval_episodes - numarul de episoade de testare
- max_frames - numarul de frame-uri maxime pe joc (pentru a limita durata jocurilor)
- agent_strategy - strategia agentului (vezi enunt: 0 - random, 1 - greedy, 2 - epsilon-greedy)
- opponent_strategy - strategia adversarului
- sleep - durata dintre cadre pentru partea de antrenare (mare pentru a se vizualiza mai repede procesul de antrenare - sau mica pentru a permite antrenarea mai rapida sau mai multe episoade) - pentru etapa de testare timpul se reseteaza si se poate vizualiza meciurile. Pe ecran sunt afisate (in terminal) starea jocului si mai multe informatii (cum ar fi scorul). 
Se pot modifica si alti parametri, cum ar fi: 
- table_width sau table_height - dimensiunile tablei (terenului)
- paddle_size - dimensiunea paletelor. 