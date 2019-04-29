#%% [markdown]
# ## Install a pip package in the current Jupyter kernel

#%%
import sys
get_ipython().system('{sys.executable} -m pip install pokebase')

#%% [markdown]
# ## Import PokeAPI wrapper library for  Python 3

#%%
import pokebase as pb

#%% [markdown]
# ## Quick lookup

#%%
rayquaza = pb.pokemon('rayquaza')
print(rayquaza.height)
print(rayquaza.weight)


#%%
rayquaza.types


#%%
rayquaza.stats

#%% [markdown]
# ## Fetch txt file from Smogon

#%%
from urllib.request import urlopen
import json

data = urlopen("https://www.smogon.com/stats/2019-03/gen7ubers-0.txt")
usage = []
for line in data:
  decoded = line.decode('utf-8')
  decoded = decoded.replace(" ", "")
  if decoded.startswith('|'):
    # usage - weighted based on matchmaking rating
    # raw - unweighted usage (on team)
    # real - actually used in battle
    decodedList = decoded.split('|')[1:-1]
    decodedList.pop(2) # remove usage %
    decodedList.pop() # remove real
    decodedList.pop() # remove real %
    usage.append(decodedList)


#%%
usage

#%% [markdown]
# ## Use pandas to visualize Smogon competitive usage data

#%%
import pandas as pd


#%%
smogon_df = pd.DataFrame(usage[1:], columns=usage[0])
smogon_df

# usage - weighted based on matchmaking rating
# raw - unweighted usage (on team)
# real - actually used in battle


#%%
statsDic = {}
for pokemon in smogon_df['Pokemon']:
  pokemon_stats = []
  pokemon_info = pb.pokemon(pokemon.lower())
  for i in (pokemon_info.stats):
    pokemon_stats.append(str(i)[14:17])
  statsDic[pokemon] = pokemon_stats

#%% [markdown]
# ## Obtain list of legendary and mystical pokemon from Bulbapedia

#%%
import requests
from bs4 import BeautifulSoup

# scrape list of legendary and mystical pokemon from bulbapedia
page = requests.get("https://bulbapedia.bulbagarden.net/wiki/Legendary_Pok%C3%A9mon")
soup = BeautifulSoup(page.content, 'html.parser')

# list of <a> tags of legendary pokemon
a_list = soup.select('td a[title*=(Pokémon)]')

# extract text from <a> tags
legend_list = [lp.get_text() for lp in a_list]

# data cleaning: replace whitespace with hyphen, remove colon
legend_list = [p.lower().replace(' ', '-').replace(':', '') for p in legend_list]
legend_list

#%% [markdown]
# ## Get itemized list for pokemon stats

#%%
pd.read_csv('statsDF.csv')


#%%
# Only run if you need the DF in the code itself, the cell above should retrieve the file
# import re
# pokemonList = []
# pokemonList.append(['ID', 'Pokemon', 'Legendary', 'Stat Total', 'ATK Sum', 'DEF Sum', 'Height', 'Weight'])

# for pokemonID in range(1,812):
#   pokemon_stats = []
#   pokemon_info = pb.pokemon(pokemonID)

#   pokemon_stats.append(pokemonID) # Add ID
#   pokemon_stats.append(pokemon_info.name) # Add Name
#   pokemon_stats.append(pokemon_info.name in legend_list) # Add Legendary or Not
#   pokemon_stats.extend([0,1,2]) # Add categories for stat totals
#   pokemon_stats.append(pokemon_info.height) # Add Height
#   pokemon_stats.append(pokemon_info.weight) # Add Weight

#   print(pokemonID)
#   j = 0 # Counter because I didnt want to change my code anymore
#   for i in (pokemon_info.stats):
#     stringStats = str(i)
#     value = [int(s) for s in re.findall(r'\b\d+\b', stringStats)[:1]]
#     pokemon_stats[3] += value[0]
#     pokemon_stats[4+(j%2)] += value[0]
#     j += 1

#   pokemonList.append(pokemon_stats)

# statsDF = pd.DataFrame(pokemonList[1:], columns=pokemonList[0])
# statsDF.to_csv ('./statsDF.csv', index = None, header=True)

# statsDF


#%% [markdown]
# ## After scraping and cleaning, test for validity by searching for each name in the API

#%%
for p in legend_list:
  try:
    pb.pokemon(p)
  except ValueError:
    print("Cannot find", p)

#%% [markdown]
# ## The above Pokemon have alternate forms and we must handle each manually
#
# P.S. Meltan and Melmetal haven't been added to the database at the moment. https://github.com/PokeAPI/pokeapi/issues/414

#%%
# deoxys: deoxys-normal, deoxys-attack, deoxys-defense, deoxys-speed
try:
  legend_list.remove('deoxys')
  legend_list.extend(['deoxys-normal', 'deoxys-attack', 'deoxys-defense', 'deoxys-speed'])
except ValueError:
  print('Error')

# giratina: giratina-altered, giratina-origin
try:
  legend_list.remove('giratina')
  legend_list.extend(['giratina-altered', 'giratina-origin'])
except ValueError:
  print('Error')

# shaymin: shaymin-land, shaymin-sky
try:
  legend_list.remove('shaymin')
  legend_list.extend(['shaymin-land', 'shaymin-sky'])
except ValueError:
  print('Error')

# tornadus: tornadus-incarnate, tornadus-therian
try:
  legend_list.remove('tornadus')
  legend_list.extend(['tornadus-incarnate', 'tornadus-therian'])
except ValueError:
  print('Error')

# thundurus: thundurus-incarnate, thundurus-therian
try:
  legend_list.remove('thundurus')
  legend_list.extend(['thundurus-incarnate', 'thundurus-therian'])
except ValueError:
  print('Error')

# landorus: landorus-incarnate, landorus-therian
try:
  legend_list.remove('landorus')
  legend_list.extend(['landorus-incarnate', 'landorus-therian'])
except ValueError:
  print('Error')

# keldeo: keldeo-ordinary, keldeo-resolute
try:
  legend_list.remove('keldeo')
  legend_list.extend(['keldeo-ordinary', 'keldeo-resolute'])
except ValueError:
  print('Error')

# meloetta: meloetta-aria, meloetta-pirouette
try:
  legend_list.remove('meloetta')
  legend_list.extend(['meloetta-aria', 'meloetta-pirouette'])
except ValueError:
  print('Error')

# meltan: remove for now
try:
  legend_list.remove('meltan')
except ValueError:
  print('Error')

# melmetal: remove for now
try:
  legend_list.remove('melmetal')
except ValueError:
  print('Error')

#%% [markdown]
# ## Test again for validity

#%%
for p in legend_list:
  try:
    pb.pokemon(p)
  except ValueError:
    print("Cannot find", p)

#%% [markdown]
# ## Obtain list of types

#%%
# scrape list of legendary and mystical pokemon from bulbapedia
page = requests.get("https://bulbapedia.bulbagarden.net/wiki/Type")
soup = BeautifulSoup(page.content, 'html.parser')

# list of <a> tags of types
a_list = soup.select('td a[title*=(type)]')

# extract text from <a> tags
type_list = [lp.get_text() for lp in a_list]

# ignore ??? type
type_list = type_list[:-1]
type_list


#%%
pstat = []
for a in legend_list:
  pstat.append()




rayquaza = pb.pokemon('rayquaza')
print(rayquaza.height)
print(rayquaza.weight)



