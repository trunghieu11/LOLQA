"""
Sample Data Collector - Fallback to hardcoded sample data.
Used when external data sources are unavailable.
"""
from typing import List
from langchain_core.documents import Document
from data_sources.base_collector import BaseDataCollector
from utils import logger


class SampleDataCollector(BaseDataCollector):
    """
    Provides sample/hardcoded data as fallback.
    This is the original data collector logic.
    """
    
    def get_name(self) -> str:
        """Get collector name"""
        return "SampleData"
    
    def collect(self) -> List[Document]:
        """
        Create sample League of Legends data.
        
        Returns:
            List of Document objects with sample data
        """
        logger.info("Using sample data collector (fallback)")
        
        documents = []
        
        # Sample champion data
        champions = [
            {
                "name": "Ahri",
                "role": "Mage/Assassin",
                "description": "Ahri is a mobile mage-assassin hybrid who uses her charm and mobility to outplay opponents.",
                "abilities": {
                    "Q": "Orb of Deception - Sends out an orb that deals magic damage on the way out and true damage on the way back.",
                    "W": "Fox-Fire - Summons three fox-fires that target nearby enemies.",
                    "E": "Charm - Blows a kiss that charms the first enemy hit, causing them to walk harmlessly towards Ahri.",
                    "R": "Spirit Rush - Dashes forward and fires essence bolts, can be cast up to 3 times."
                },
                "playstyle": "Ahri excels at picking off isolated targets and escaping dangerous situations with her ultimate."
            },
            {
                "name": "Yasuo",
                "role": "Fighter/Assassin",
                "description": "Yasuo is a melee carry who relies on critical strikes and mobility to dominate teamfights.",
                "abilities": {
                    "Q": "Steel Tempest - Thrusts forward, dealing damage. After two casts, the third creates a tornado.",
                    "W": "Wind Wall - Creates a wall that blocks all enemy projectiles for 4 seconds.",
                    "E": "Sweeping Blade - Dashes through a target enemy, dealing damage. Cannot be used on the same target for a few seconds.",
                    "R": "Last Breath - Blinks to an airborne enemy champion, dealing damage and keeping them in the air."
                },
                "playstyle": "Yasuo requires precise positioning and timing to maximize his damage output and survivability."
            },
            {
                "name": "Jinx",
                "role": "Marksman",
                "description": "Jinx is a hyper-carry marksman who excels at dealing massive area damage in teamfights.",
                "abilities": {
                    "Q": "Switcheroo! - Switches between Pow-Pow (machine gun) and Fishbones (rocket launcher).",
                    "W": "Zap! - Fires a shock blast that slows and reveals the first enemy hit.",
                    "E": "Flame Chompers! - Throws three chompers that explode when enemies step on them.",
                    "R": "Super Mega Death Rocket! - Fires a global rocket that deals more damage the farther it travels."
                },
                "playstyle": "Jinx scales incredibly well into late game and can single-handedly win teamfights with proper positioning."
            },
            {
                "name": "Thresh",
                "role": "Support",
                "description": "Thresh is a tanky support who excels at crowd control and protecting allies.",
                "abilities": {
                    "Q": "Death Sentence - Throws his scythe, pulling himself and the enemy closer together.",
                    "W": "Dark Passage - Throws a lantern that allies can click to dash to Thresh.",
                    "E": "Flay - Sweeps his chain, knocking enemies in the direction of the swing.",
                    "R": "The Box - Creates walls of spectral energy that slow and damage enemies who pass through."
                },
                "playstyle": "Thresh is a playmaking support who can initiate fights and save teammates with his utility."
            },
            {
                "name": "Lee Sin",
                "role": "Fighter/Assassin",
                "description": "Lee Sin is a highly mobile jungler known for his early game pressure and outplay potential.",
                "abilities": {
                    "Q": "Sonic Wave / Resonating Strike - Fires a skillshot that marks enemies, can recast to dash to them.",
                    "W": "Safeguard / Iron Will - Dashes to an ally or ward, gaining a shield. Can activate for lifesteal and spell vamp.",
                    "E": "Tempest / Cripple - Slams the ground, dealing damage and revealing enemies. Can recast to slow.",
                    "R": "Dragon's Rage - Kicks an enemy champion away, dealing damage and knocking back all enemies hit."
                },
                "playstyle": "Lee Sin requires high mechanical skill and game knowledge to maximize his impact throughout the game."
            }
        ]
        
        # Convert champions to documents
        for champ in champions:
            content = f"""
Champion: {champ['name']}
Role: {champ['role']}
Description: {champ['description']}

Abilities:
- Q: {champ['abilities']['Q']}
- W: {champ['abilities']['W']}
- E: {champ['abilities']['E']}
- R: {champ['abilities']['R']}

Playstyle: {champ['playstyle']}
"""
            documents.append(Document(
                page_content=content.strip(),
                metadata={"champion": champ['name'], "role": champ['role'], "type": "champion", "source": "sample"}
            ))
        
        # Add game mechanics
        game_mechanics = [
            Document(
                page_content="""
League of Legends Game Mechanics:

Laning Phase: The early game phase where players farm minions and trade with opponents in their assigned lanes.
Objectives: Important map locations like Dragon, Baron Nashor, and Rift Herald that provide team-wide benefits.
Teamfighting: Coordinated group combat where teams fight for objectives or map control.
Positioning: Critical skill of placing your champion in optimal locations during fights to maximize effectiveness while minimizing risk.
Vision Control: Using wards and sweepers to control map visibility and prevent ganks.
""",
                metadata={"type": "game_mechanics", "source": "sample"}
            ),
            Document(
                page_content="""
Item Builds in League of Legends:

Core Items: Essential items that define a champion's playstyle and power spikes.
Situational Items: Items built based on the enemy team composition and game state.
Boots: Movement speed items that also provide combat stats. Different types for different roles.
Mythic Items: Powerful items that define a champion's build path and provide unique effects.
Legendary Items: High-tier items that complement the mythic item choice.
""",
                metadata={"type": "items", "source": "sample"}
            ),
            Document(
                page_content="""
Ranked System:

Ranked Tiers: Iron, Bronze, Silver, Gold, Platinum, Emerald, Diamond, Master, Grandmaster, Challenger
LP (League Points): Points earned or lost based on match outcomes
Promotion Series: Best-of series to advance to the next tier
MMR (Matchmaking Rating): Hidden rating that determines matchmaking
""",
                metadata={"type": "ranked", "source": "sample"}
            )
        ]
        
        documents.extend(game_mechanics)
        logger.info(f"Created {len(documents)} sample documents")
        return documents

