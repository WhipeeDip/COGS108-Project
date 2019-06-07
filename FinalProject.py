#%% [markdown]
# ## Import packages

#%%
import sys
get_ipython().system('{sys.executable} -m pip install pokebase')

import pokebase as pb
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import pandas as pd
import math
import matplotlib.pyplot as plt

#%% [markdown]
# # Part 1: Data Collection and Cleaning
#%% [markdown]
# ## Obtain list of legendary and mystical Pokémon from Bulbapedia

#%%
# scrape list of legendary and mystical pokemon from bulbapedia
page = requests.get("https://bulbapedia.bulbagarden.net/wiki/Legendary_Pok%C3%A9mon")
soup = BeautifulSoup(page.content, 'html.parser')

# list of <a> tags of legendary pokemon
a_list = soup.select('td[style*="background: #e6e6ff"] a')

# extract text from <a> tags
legend_list = [lp.get_text() for lp in a_list]

# data cleaning: replace whitespace with hyphen, remove colon
legend_list = [p.lower().replace(' ', '-').replace(':', '') for p in legend_list]
legend_list_smogon = legend_list.copy()
legend_list

#%% [markdown]
# ## After scraping and cleaning, test for validity by searching for each name in the API

#%%
for p in legend_list:
    try:
        pb.pokemon(p)
    except ValueError:
        print("Cannot find", p)

#%% [markdown]
# ## The above Pokémon have alternate forms and we must handle each manually
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
# ## Get CSV file for all Pokémon info

#%%
# #Only run if you need the DF in the code itself, the cell above should retrieve the file
# import re
# pokemonList = []
# pokemonList.append(['ID', 'Pokemon', 'Legendary', 'Stat Total', 'ATK Sum', 'DEF Sum', 'Height', 'Weight', 'Type 1', 'Type 2'])

# for pokemonID in range(1,808):
#   pokemon_stats = []
#   pokemon_info = pb.pokemon(pokemonID)

#   pokemon_stats.append(pokemonID) # Add ID
#   pokemon_stats.append(pokemon_info.name) # Add Name
#   pokemon_stats.append(pokemon_info.name in legend_list) # Add Legendary or Not
#   pokemon_stats.extend([0,0,0]) # Add categories for stat totals
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

#   for i in pokemon_info.types:
#     stringType = str(i)
#     typing = re.findall('\'name\': \'(.+?)\'', stringType)
#     pokemon_stats.append(typing[0])


#   if len(pokemon_info.types) == 1:
#     pokemon_stats.append("N/A")

#   pokemonList.append(pokemon_stats)

# statsDF = pd.DataFrame(pokemonList[1:], columns=pokemonList[0])
# statsDF.to_csv ('./statsDF.csv', index = None, header=True)

# statsDF


#%%
df = pd.read_csv('statsDF.csv')
df

#%% [markdown]
# ## Obtain list of Pokémon types

#%%
# scrape list of pokemon types from bulbapedia
page = requests.get("https://bulbapedia.bulbagarden.net/wiki/Type")
soup = BeautifulSoup(page.content, 'html.parser')

# list of <a> tags of types
a_list = soup.select('td a[title*="(type)"]')

# extract text from <a> tags
type_list = [lp.get_text() for lp in a_list]

# ignore ??? type
type_list = type_list[:-1]
type_list

#%% [markdown]
# ## Fetch txt file from Smogon

#%%
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

# real - actually used in battle
# raw - unweighted usage (on team)
# usage - weighted based on matchmaking rating
smogon_df = pd.DataFrame(usage[1:], columns=usage[0])
smogon_df

#%% [markdown]
# ## Match legendary list to Smogon names

#%%
legend_list_smogon.extend(['deoxys-attack', 'deoxys-defense', 'deoxys-speed'])
legend_list_smogon.extend(['giratina-origin'])
legend_list_smogon.extend(['shaymin-sky'])
legend_list_smogon.extend(['tornadus-therian'])
legend_list_smogon.extend(['thundurus-therian'])
legend_list_smogon.extend(['landorus-therian'])

try:
    legend_list_smogon.remove('meltan')
except ValueError:
    print('Error')

try:
    legend_list_smogon.remove('melmetal')
except ValueError:
    print('Error')

# smogon pokemon names are captialized
legend_list_smogon = [str.title(name) for name in legend_list_smogon]

try:
    legend_list_smogon.remove('Tapu-Koko')
    legend_list_smogon.extend(['TapuKoko'])
except ValueError:
    print('Error')

try:
    legend_list_smogon.remove('Tapu-Lele')
    legend_list_smogon.extend(['TapuLele'])
except ValueError:
    print('Error')

try:
    legend_list_smogon.remove('Tapu-Bulu')
    legend_list_smogon.extend(['TapuBulu'])
except ValueError:
    print('Error')

try:
    legend_list_smogon.remove('Tapu-Fini')
    legend_list_smogon.extend(['TapuFini'])
except ValueError:
    print('Error')

try:
    legend_list_smogon.remove('Type-Null')
    legend_list_smogon.extend(['Type:Null'])
except ValueError:
    print('Error')

#%% [markdown]
# # Part 2: Smogon Competitive Usage Data Analysis
#%% [markdown]
# Smogon is a database for people who are interested in competitive Pokémon battles. Players utilize this data to form strategies to play against other competitors. The database displays advantages and disadvantages of each Pokémon. For example, Pokémon of the fire type are weak against water types, likewise water types are extremely effective against fire types.
#%% [markdown]
# ## Use pandas to visualize Smogon competitive usage data

#%%
# print(len(legend_list_smogon)) = 76

# convert string to floats
smogon_df['Raw'] = smogon_df['Raw'].astype(int)

# using legend_list_smogon, split dataframe
smogon_legend_df = smogon_df[smogon_df['Pokemon'].str.contains('|'.join(legend_list_smogon))].copy()
smogon_legend_df['Rank'] = smogon_legend_df['Rank'].astype(int)
smogon_normal_df = smogon_df[-smogon_df['Pokemon'].str.contains('|'.join(legend_list_smogon))].copy()
smogon_normal_df['Rank'] = smogon_normal_df['Rank'].astype(int)

# plot raw usage of legendaries vs normal
smogon_usage_graph_data = [
  ['Legendaries', smogon_legend_df['Raw'].sum()],
  ['Normal', smogon_normal_df['Raw'].sum()]
]
smogon_usage_graph_df = pd.DataFrame(smogon_usage_graph_data, columns = ['Type', 'Raw Usage'])
ax_smogon_usage = smogon_usage_graph_df.plot.bar(x = 'Type', y = 'Raw Usage', title = 'Smogon Ubers Overall Raw Usage',
  legend = False, color = ['orange', 'blue'])
ax_smogon_usage.set_xlabel('Type')
ax_smogon_usage.set_ylabel('Raw Usage')
plt.show()

#%% [markdown]
# We use pandas to create a bar graph indicating the usage of certain categories of Pokémon over another. The categories used are Legendaries and Non-Legendaries. With this visualization, we can see that Legendaries are used a considerable percentage more than Non-Legendary Pokémons. We speculate that this is due to variables of the Pokémon, such as physical characteristics, and will continue to draw from visualizations to understand why this is the case.

#%%
# plot raw usage against rank
plt.scatter(smogon_df['Rank'], smogon_df['Raw'], color = 'gray')
plt.title('Smogon Ubers Rank vs. Raw Usage')
plt.xlabel('Rank')
plt.ylabel('Raw Usage')
plt.xticks([0, *range(99, len(smogon_df), 100)])
plt.show()

#%% [markdown]
# The next visualization is a negative exponential graph, with the x-axis as the Pokémon rank and the y-axis as the Raw Usage by players. We create this graph using matplotlib with the Rank as the position within a hierarchical system - from best to worst rank. Raw Usage is the same data used in the last graph - showing how often the Pokémon is used in the competitive scene. Analyzing this graph, we can see that there is a correlation between high ranking and the frequency the Pokémon is used.

#%%
# get the makeup of the top x% used
smogon_top_count = math.ceil(len(smogon_df) * 0.1) # used for the cutoffs
smogon_num_legend = (smogon_legend_df[smogon_legend_df['Rank'] <= smogon_top_count])['Rank'].size
smogon_num_normal = (smogon_normal_df[smogon_normal_df['Rank'] <= smogon_top_count])['Rank'].size
smogon_num_graph_data = [
  ['Legendaries ({})'.format(smogon_num_legend), smogon_num_legend],
  ['Normal ({})'.format(smogon_num_normal), smogon_num_normal]
]
smogon_num_graph_df = pd.DataFrame(smogon_num_graph_data, columns = ['Type', 'Count'])
ax_smogon_num = smogon_num_graph_df.plot.bar(x = 'Type', y = 'Count', title = 'Smogon Ubers Top 10% ({}) Used Composition'.format(smogon_top_count),
  legend = False, color = ['orange', 'blue'])
ax_smogon_num.set_xlabel('Type')
ax_smogon_num.set_ylabel('Number')
plt.show()

#%% [markdown]
# Although the above indicates that Legendaries are used a reasonable amount more than Non-Legendaries, we see a different result for the top 10% of competitors. The top 10% players instead use Non-Legendary Pokémons more, but only by a small amount. The slight difference is due to the smaller sample size - as it is only the top percentage of users.
#%% [markdown]
# # Part 3: Physical Attributes Analysis
#%% [markdown]
# ## 3.1 Weight vs. Height
#
# Using a scatter plots, we can examine the relationship between the height and weight of all Pokémon. The plots below show how most Pokémon's measurements concentrate toward the bottom left corner, whereas there are only a few outliers.
#%% [markdown]
# ### Non-legendaries

#%%
df[~df['Pokemon'].isin(legend_list)][['Height', 'Weight']].plot.scatter('Weight', 'Height').set(xlabel='Weight (hectograms)', ylabel='Height (decimetres)')

#%% [markdown]
# At first glance, we can see in the scatter plot that the bulk of Non-Legendary Pokémons’ Height and Weight are concentrated in the bottom left. This indicates that Non-Legendaries tend to be smaller in size.
#%% [markdown]
# ### Legendaries

#%%
df[df['Pokemon'].isin(legend_list)][['Height', 'Weight']].plot.scatter('Weight', 'Height', c='orange').set(xlabel='Weight (hectograms)', ylabel='Height (decimetres)')

#%% [markdown]
# For this scatterplot, the first thing to note is that there is significantly less Legendary Pokémons than Non-Legendaries. Additionally, we can see that the Height and Weight for Legendaries vary extremely - with most being in the larger range.
#%% [markdown]
# ### Combined

#%%
ax = df[~df['Pokemon'].isin(legend_list)][['Height', 'Weight']].plot('Weight', 'Height', kind='scatter')
df[df['Pokemon'].isin(legend_list)][['Height', 'Weight']].plot('Weight', 'Height', kind='scatter', c='orange', ax=ax).set(xlabel='Weight (hectograms)', ylabel='Height (decimetres)')

#%% [markdown]
# Combining both scatter plots shows that although Legendary Pokémons are larger in size, there are exceptions to this case. An outlier example being that there is a Non-Legendary that is the tallest out of all Pokémon. Another irrational outlier is that there is a Legendary that is short but is the heaviest Pokémon overall.
#%% [markdown]
# ### Means of Weight and Height
#
# Legendary mean: maroon
# Regular mean: cyan

#%%
# legendary average height
l_h_mean = df[df['Pokemon'].isin(legend_list)]['Height'].mean()

# legendary average weight
l_w_mean = df[df['Pokemon'].isin(legend_list)]['Weight'].mean()

# regular average height
r_h_mean = df[~df['Pokemon'].isin(legend_list)]['Height'].mean()

# regular avaerage weight
r_w_mean = df[~df['Pokemon'].isin(legend_list)]['Weight'].mean()

# calculate means
df_l_mean = pd.DataFrame({"Weight":[l_w_mean], "Height":[l_h_mean]})
df_r_mean = pd.DataFrame({"Weight":[r_w_mean], "Height":[r_h_mean]})
print('Legendary Pokemon average weight: ', round(df_l_mean.loc[0]['Weight'], 2), '; average height: ', round(df_l_mean.loc[0]['Height'], 2))
print('Regular Pokemon average weight: ', round(df_r_mean.loc[0]['Weight'], 2), '; average height: ', round(df_r_mean.loc[0]['Height'], 2))

# plot
ax = df[~df['Pokemon'].isin(legend_list)][['Height', 'Weight']].plot('Weight', 'Height', kind='scatter')
df[df['Pokemon'].isin(legend_list)][['Height', 'Weight']].plot('Weight', 'Height', kind='scatter', c='orange', ax=ax)
df_l_mean.plot.scatter('Weight', 'Height', c="maroon", s=140, ax = ax)
df_r_mean.plot.scatter('Weight', 'Height', c="cyan", s=140, ax = ax).set(xlabel='Weight (hectograms)', ylabel='Height (decimetres)')

#%% [markdown]
# We plot the mean Height and Weight data to display the combined average Height & Weight of Legendary and Non-Legendary, individually, amongst all Pokémons. This data also includes outliers but they do not affect the data substantially, as there are many other data points we are analyzing.
#%% [markdown]
# Additionally from the plot above, we can conclude that the average legendary Pokémon is likely to be taller and heavier than the average non-legendary Pokémon.
#%% [markdown]
# ## 3.2 Types
#%% [markdown]
# Lets identify what typings legendary Pokemon typically are. First we need to separate the legendary data from the overall dataframe
#%% [markdown]
# ### Make a list of Pokémon Types

#%%
legendsDf = df[df['Pokemon'].isin(legend_list)]

legend_types = list(legendsDf['Type 1']) + list(legendsDf['Type 2'])
types = list(df['Type 1']) + list(df['Type 2'])

legendTypeCount = pd.Series(legend_types).value_counts().append(pd.Series([0],['poison']))
regularTypeCount = pd.Series(types).value_counts()


#%%
legendsDf

#%% [markdown]
# Kind of hard to read, so lets just get the counts instead of individual pokemon.

#%%
legendTypeCount


#%%
legendPlot = legendTypeCount.plot(kind='bar', title='Legendary Pokemon Typing', yticks=range(0,25,5), color="orange")
xstuff = legendPlot.set_xlabel("Typing")
ystuff = legendPlot.set_ylabel("Count")

#%% [markdown]
# Here we can see that psychic dominate the typings for legendary Pokemon, doubling the counts for any other type. From there it slowly declines until we get to poison, where we can see 0 Pokemon have poison typing. Surprisingly, dragon isnt the most frequent typing, which somewhat subverted our expectations but is reasonable once we thought back onto what legendary Pokemon there were.

#%%
regularTypeCount


#%%
normalPlot = regularTypeCount.plot(kind='bar', title='All Pokemon Typing', yticks=range(0,150,10),  color="blue")
xstuff = normalPlot.set_xlabel("Typing")
ystuff = normalPlot.set_ylabel("Count")

#%% [markdown]
# Now with regular pokemon, we can see that its a lot more evenly spread out. Water has a plurality of the typings but is not as dominant as psychic was for legendaries. Poison finds itself near the middle of the type distribution, suggesting that the lack of a legendary Pokemon being poison typed may be intentional rather than through sheer chance.

#%%
typeCompDf = legendTypeCount.to_frame()
typeCompDf = typeCompDf.merge(regularTypeCount.to_frame(), left_index=True, right_index=True)
typeCompDf.columns = ['Legendary','Normal']
typeCompDf=typeCompDf.reindex(columns=['Normal','Legendary'])
normFirst = regularTypeCount.to_frame()
normFirst = normFirst.merge(legendTypeCount.to_frame(), left_index = True, right_index = True)
normFirst.columns = ['Normal','Legendary']


#%% [markdown]
# Now lets compare the two side-by-side.

#%%
typeCompDf


#%%
normFirst


#%%
import matplotlib.pyplot as plt
overallPlot = typeCompDf.plot(kind='bar', title ="Type Distribution")
xstuff = overallPlot.set_xlabel("Typing")
ystuff = overallPlot.set_ylabel("Count")


#%%
normFirstPlot = normFirst.plot(kind='bar', title ="Type Distribution")
xstuff = normFirstPlot.set_xlabel("Typing")
ystuff = normFirstPlot.set_ylabel("Count")

#%% [markdown]
# Through these two graphs, we can see that there only seems to be a small correlation between the typing for all Pokemon in general, and the typing for legendary Pokemon (seen in flying, water, and psychic for both graphs). This suggests that legendary Pokemon are made without this distribution in mind, and more made to appeal to the abstract idea of legendary that most people view as dragons or psychic beings.
#%% [markdown]
# # Part 4: Pokémon Stats Analysis

#%%
# Display plots directly in the notebook instead of in a new window
get_ipython().run_line_magic('matplotlib', 'inline')

# Import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure libraries
# The seaborn library makes plots look nicer
sns.set()
sns.set_context('talk')

# Don't display too many rows/cols of DataFrames
pd.options.display.max_rows = 9
pd.options.display.max_columns = 10

# Round decimals when displaying DataFrames
pd.set_option('precision', 2)

#%% [markdown]
# Reading the CSV

#%%
df_poke = pd.read_csv("statsDF.csv")
df_poke

#%% [markdown]
# Dropping columns that are irrelevant to this section and splitting the dataframe into two dataframes for Legendary and NonLegendary Pokemon:

#%%
df_AD = df_poke.drop(columns = ["Height","Weight","Stat Total","Type 1","Type 2"])
df_LegsEnd = df_AD[df_AD["Legendary"] == True]
df_LegsDontEnd = df_AD[df_AD["Legendary"] == False]
df_LegsEnd

#%% [markdown]
# ### Visualizing Pokemon Distribution by Stats
#%% [markdown]
# Now that the data is organized distinctly, let's visualize the pokemon in scatterplots with their offensive stat totals on the x-axis and their defensive stat totals on the y-axis.

#%%
df_LegsEnd.plot.scatter(x="ATK Sum", y="DEF Sum", c="orange")
plt.title("Legendary Offensive vs. Defensive Stat Distribution", pad=(25))
df_LegsDontEnd.plot.scatter(x="ATK Sum", y="DEF Sum", c="b")
plt.title("NonLegendary Offensive vs. Defensive Stat Distribution", pad=(25))
plt.show()

#%% [markdown]
# In the two scatterplots above, we can observe the distribution of offensive and defensive stats on the Legendary and NonLegendary Pokemon separately. In the first scatterplot, we can already see that Legendary Pokemon tend to lean in the upper range for both offsensive and defensive stats, with the exception of a couple of outliers. In the second scatterplot, we can observe that the majority of the NonLegendary Pokemon cluster in a lower range than the Legendary Pokemon.
#
#
# Now let's see how the two groups look in the same scatterplot:

#%%
a = df_LegsDontEnd.plot.scatter(x="ATK Sum", y="DEF Sum", c="b")
b = df_LegsEnd.plot.scatter(x="ATK Sum", y="DEF Sum", c="orange", ax = a)
plt.title("Offensive vs. Defensive Stat Distribution", pad=(25))
plt.show()

#%% [markdown]
# After stacking the two scatterplots together we can observe that the majority of the Legendary Pokemon (yellow) tend to have greater stats all around. Except for a few exceptions, almost all of the Legendary Pokemon data points are in the upper right quadrant of the scatterplot such that they either have great defensive stats or greater offensive stats or even both. Only a handful of the NonLegendary Pokemon data points are in the same class as the Legendary Pokemon.
#
# However, despite that distinct difference between the two categories of Pokemon, they both seem to have populations that do not heavily skew towards either axis.
#
#
# Now, to visualize their stats as a whole and comparing their distributions, let's create another data frame to handle the "Stat Total" data and drop irrelevant columns.

#%%
df_total = df_poke.drop(columns = ["Height","Weight","DEF Sum","ATK Sum","Type 1","Type 2"])
df_total

#%% [markdown]
# Here we'll separate the data frame into two parts: Legendary and NonLegendary:

#%%
df_legtotal = df_total[df_AD["Legendary"] == True]
df_legtotal


#%%
df_nontotal = df_total[df_AD["Legendary"] == False]
df_nontotal

#%% [markdown]
# Now with the data separated, let's visualize the distributions using histograms:

#%%
df_legtotal["Stat Total"].hist(bins = 25)
plt.xlabel("Stat Total")
plt.ylabel("Pokemon")
plt.title("Legendary Total Stat Distribution", pad=(25))
plt.show()

#%% [markdown]
# In this first histogram, we plotted the distribution of Legendary Pokemon with respect to the total sum of all their core stats. Most notably, we observe that a large number of Legendary Pokemon have stat totals of around 600 and even a significant number around 700. Furthermore, we can observe that there is an outlier data point with a stat total of around 200. Altogether, the histogram shows that Legendary Pokemon have stat totals that skews to the right of the histogram, with notably high stats.

#%%
df_nontotal["Stat Total"].hist(bins = 25)
plt.xlabel("Stat Total")
plt.ylabel("Pokemon")
plt.title("NonLegendary Total Stat Distribution", pad=(25))
plt.show()

#%% [markdown]
# In this second histogram, we plotted the distribution of NonLegendary Pokemon with respect to the total sum of all their core stats. Here, we can observe that the distribution is not quite normal with its two peaks at roughly 300 and 500 and a fall-off on either end that do not have any extremeley explicit outliers. The distribution seems to be wide and does not skew in either direction in particular.
#
# Now let's see how they compare together on the same histogram:

#%%
a1 = df_nontotal["Stat Total"].hist(bins = 25)
b1 = df_legtotal["Stat Total"].hist(bins = 25, ax = a1)
plt.title("Total Stat Distribution", pad=(25))
plt.xlabel("Stat Total")
plt.ylabel("Pokemon")
plt.show()

#%% [markdown]
# In this histogram, the two categories of Pokemon are plotted together with blue representing the NonLegendary Pokemon and orange representing the Legendary Pokemon. In this histogram, the data just barely overlaps and we chose to have the Legendary population at the front because it has a smaller population and infringes less in the overlap. Here we see that the vast majority of the Legendary Pokemon distribution is significantly right skewed are almost completely to the right of the NonLegendary Pokemon distribution.
#
# To further examine the magnitude of their difference let's get their averages amost the entire population and visualize the comparison:

#%%
numNon = len(df_nontotal["Stat Total"])
numLeg = len(df_legtotal["Stat Total"])
sumNon = df_nontotal.sum(axis = 0)[3]
sumLeg = df_legtotal.sum(axis = 0)[3]
avgNon = sumNon / numNon
avgLeg = sumLeg / numLeg
print(avgNon)
print(avgLeg)


#%%
sumNonA = df_LegsDontEnd.sum(axis = 0)[3]
sumNonD = df_LegsDontEnd.sum(axis = 0)[4]
sumLegA = df_LegsEnd.sum(axis = 0)[3]
sumLegD = df_LegsEnd.sum(axis = 0)[4]
avgNonA = sumNonA / numNon
avgNonD = sumNonD / numNon
avgLegA = sumLegA / numLeg
avgLegD = sumLegD / numLeg

print(avgNonA)
print(avgNonD)
print(avgLegA)
print(avgLegD)


#%%
df = pd.DataFrame({'stats':['NonLegendary', 'Legendary'], 'val':[avgNon, avgLeg]})
ax = df.plot.bar(x='stats', y='val', rot=0)
plt.title("Legendary vs NonLegendary Total Stats", pad=(25))
plt.show()

#%% [markdown]
# We've calculated the average NonLegendary stat total to be 405 and the average Legendary stat total to be 602. For their offsensive and defensive breakdowns we have 203 and 203, and 306 and 296 respectively. As shown in the bar graph, Legendary Pokemon are found to have approximately 50% greater stats than NonLegendary Pokemon, truly earning them a "legendary" status.
#
# Now with their average offensive and defensive stats, let's revisit the scatterplot and add in points to show where their averages lie:

#%%
df_avgLeg = pd.DataFrame({"ID":["999"], "Pokemon":["Average Legendary"], "Legendary":["True"], "ATK Sum":[avgLegA], "DEF Sum":[avgLegD]})
df_avgNon = pd.DataFrame({"ID":["999"], "Pokemon":["Average NonLegendary"], "Legendary":["False"], "ATK Sum":[avgNonA], "DEF Sum":[avgNonD]})

aaa = df_LegsDontEnd.plot.scatter(x="ATK Sum", y="DEF Sum", c="b")
bbb = df_LegsEnd.plot.scatter(x="ATK Sum", y="DEF Sum", c="orange", ax = aaa)
ccc = df_avgNon.plot.scatter(x="ATK Sum", y="DEF Sum", c="cyan", s=140, ax = aaa)
ddd = df_avgLeg.plot.scatter(x="ATK Sum", y="DEF Sum", c="maroon", s=140, ax = aaa)
plt.title("Offensive vs. Defensive Stat Distribution With Average", pad=(25))
plt.show()

#%% [markdown]
# After adding a big cyan data point to represent the average NonLegendary Pokemon and a big maroon data point to represent the average Legendary Pokemon, we can easily see how Legendary Pokemon tend to be roughly 50% further from the origin (0,0) point in the scatterplot.
#
#
# With such a well-defined difference in stats in favor of Legendary Pokemon, it's no surprise they are referred to as such and tend to be more limited and significant.

#%%



