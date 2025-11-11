use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::fs::{self, File};
use std::io::{BufRead, BufReader, Write};

/// IDS operators that describe character composition (we filter these out)
/// Unicode range U+2FF0 to U+2FFF (all 16 IDS operators)
const IDS_OPERATORS: &[char] = &[
    '⿰', '⿱', '⿲', '⿳', '⿴', '⿵', '⿶', '⿷', '⿸', '⿹', '⿺', '⿻', '⿼', '⿽', '⿾', '⿿',
];

/// Character to its IDS decomposition mapping
#[derive(Debug, Serialize, Deserialize)]
pub struct CharacterDecomposition {
    pub character: String,
    pub ids: String,
    pub components: Vec<String>,
}

/// Mapping from a set of components to characters that can be formed
#[derive(Debug, Serialize, Deserialize)]
pub struct ComponentsToCharacters {
    /// Sorted component string as key (e.g., "日月" for 明)
    pub components_key: String,
    /// Characters that can be formed from these components
    pub characters: Vec<String>,
}

/// Game data containing all necessary mappings
#[derive(Debug, Serialize, Deserialize)]
pub struct GameData {
    /// Character → decomposition mapping
    pub char_to_decomposition: HashMap<String, CharacterDecomposition>,
    /// Components → characters mapping (sorted components as key)
    pub components_to_chars: HashMap<String, Vec<String>>,
    /// Set of all leaf components used in HSK words
    pub allowed_components: HashSet<String>,
    /// HSK level → words mapping
    pub hsk_words: HashMap<u8, Vec<String>>,
}

/// Parse IDS file and return character → IDS mapping
/// Handles both Unicode format (U+XXXX) and entity reference format (CDP-XXXX, J90-XXXX, etc.)
pub fn parse_ids_file(path: &str) -> Result<HashMap<String, String>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut ids_map = HashMap::new();

    for line in reader.lines() {
        let line = line?;

        // Skip comments and empty lines
        if line.starts_with('#') || line.starts_with(";;") || line.trim().is_empty() {
            continue;
        }

        // Format: U+XXXX<tab>CHAR<tab>IDS or ENTITY<tab>&ENTITY;<tab>IDS
        let parts: Vec<&str> = line.split('\t').collect();
        if parts.len() >= 3 {
            let character = parts[1].to_string();
            let ids = parts[2].to_string();

            // Only add if IDS is different from the character itself (has decomposition)
            if ids != character {
                ids_map.insert(character, ids);
            }
        }
    }

    Ok(ids_map)
}

/// Load all IDS files and merge them
/// Includes entity reference files (CDP) to resolve entity references
/// NOTE: JIS file removed because it contains non-standard character references
pub fn load_all_ids() -> Result<HashMap<String, String>> {
    let mut combined = HashMap::new();

    let ids_files = vec![
        "ids/IDS-UCS-Basic.txt",
        "ids/IDS-UCS-Ext-A.txt",
        "ids/IDS-CDP.txt",           // CDP entity references
        // "ids/IDS-JIS-X0208-1990.txt", // REMOVED: Contains non-standard references like &I-J90-3065;
    ];

    for file_path in ids_files {
        match parse_ids_file(file_path) {
            Ok(ids_map) => {
                println!("  ✅ Loaded {} from {}", ids_map.len(), file_path);
                combined.extend(ids_map);
            }
            Err(e) => {
                eprintln!("  ⚠️  Warning: Could not load {}: {}", file_path, e);
            }
        }
    }

    println!("  📊 Total unique IDS entries: {}", combined.len());
    Ok(combined)
}

/// Check if an entity reference is an extended IDC operator (non-standard combining character)
/// These should be filtered out as they're operators, not actual components
/// Pattern: &U-i###+ followed by a 2FF hex code (IDS operators range)
fn is_extended_idc(entity: &str) -> bool {
    // Extended IDC entity references follow the pattern &U-i###+2FFx; where x is 0-F
    // These are IDS operators (U+2FF0 to U+2FFF range), not components
    // Examples: &U-i001+2FF1;, &U-i002+2FF1;, &U-i001+2FFB;
    //
    // BUT: &U-i001+20541; is NOT an operator - it's a variant of U+20541
    // Only filter if the code point is in the 2FF0-2FFF range (IDS operators)
    if !entity.starts_with("&U-i") {
        return false;
    }

    // Extract the hex code after the '+'
    if let Some(plus_idx) = entity.find('+') {
        let after_plus = &entity[plus_idx + 1..];
        // Check if it starts with "2FF" (IDS operator range)
        if let Some(semicolon_idx) = after_plus.find(';') {
            let hex_code = &after_plus[..semicolon_idx];
            return hex_code.starts_with("2FF");
        }
    }

    false
}

/// Extract components from IDS string (filtering out operators and extended IDCs)
/// Properly handles entity references like &CDP-8B7A; as single components
fn extract_components_from_ids(ids: &str) -> Vec<String> {
    let mut components = Vec::new();
    let mut current = String::new();
    let mut in_entity = false;

    for c in ids.chars() {
        if c == '&' {
            // Start of entity reference
            in_entity = true;
            current.push(c);
        } else if c == ';' && in_entity {
            // End of entity reference
            current.push(c);

            // Filter out extended IDC entity references
            if !is_extended_idc(&current) {
                components.push(current.clone());
            }

            current.clear();
            in_entity = false;
        } else if in_entity {
            // Inside entity reference
            current.push(c);
        } else if !IDS_OPERATORS.contains(&c) {
            // Regular character (not an operator)
            components.push(c.to_string());
        }
        // Skip IDS operators
    }

    // Handle case where entity wasn't closed (shouldn't happen with valid data)
    if !current.is_empty() {
        components.push(current);
    }

    components
}

/// Recursively decompose a character to its leaf components
pub fn decompose_to_leaves(
    character: &str,
    ids_map: &HashMap<String, String>,
    visited: &mut HashSet<String>,
) -> HashSet<String> {
    let mut leaves = HashSet::new();

    // Prevent infinite recursion
    if visited.contains(character) {
        return leaves;
    }
    visited.insert(character.to_string());

    // If no IDS entry, this is a leaf component
    if let Some(ids) = ids_map.get(character) {
        let components = extract_components_from_ids(ids);

        for component in components {
            // Recursively decompose each component
            let sub_leaves = decompose_to_leaves(&component, ids_map, visited);
            if sub_leaves.is_empty() {
                // This component is a leaf
                leaves.insert(component);
            } else {
                // Add all sub-leaves
                leaves.extend(sub_leaves);
            }
        }
    } else {
        // No decomposition available, this is a leaf
        leaves.insert(character.to_string());
    }

    leaves
}

/// Build character decomposition data
pub fn build_char_decompositions(
    ids_map: &HashMap<String, String>,
) -> HashMap<String, CharacterDecomposition> {
    let mut decompositions = HashMap::new();

    for (character, ids) in ids_map {
        let components = extract_components_from_ids(ids);

        decompositions.insert(
            character.clone(),
            CharacterDecomposition {
                character: character.clone(),
                ids: ids.clone(),
                components,
            },
        );
    }

    decompositions
}

/// Build reverse mapping: components → characters
/// This includes BOTH direct components AND all possible subsets of leaf components
pub fn build_components_to_chars(
    decompositions: &HashMap<String, CharacterDecomposition>,
    ids_map: &HashMap<String, String>,
) -> HashMap<String, Vec<String>> {
    let mut components_map: HashMap<String, Vec<String>> = HashMap::new();

    for (character, decomp) in decompositions {
        // Add direct components mapping
        let mut sorted_components = decomp.components.clone();
        sorted_components.sort();
        let key = sorted_components.join("");

        components_map
            .entry(key)
            .or_insert_with(Vec::new)
            .push(character.clone());

        // ALSO add leaf components mapping
        // This allows building characters from their leaf components
        let mut visited = HashSet::new();
        let leaf_components = decompose_to_leaves(character, ids_map, &mut visited);

        // Convert HashSet to Vec for comparison and sorting
        let mut leaf_vec: Vec<String> = leaf_components.into_iter().collect();
        if !leaf_vec.is_empty() && leaf_vec != decomp.components {
            leaf_vec.sort();
            let leaf_key = leaf_vec.join("");

            components_map
                .entry(leaf_key)
                .or_insert_with(Vec::new)
                .push(character.clone());
        }
    }

    components_map
}

/// Extract all leaf components from HSK words
pub fn extract_allowed_components(
    hsk_words: &HashMap<u8, Vec<String>>,
    ids_map: &HashMap<String, String>,
) -> HashSet<String> {
    let mut allowed_components = HashSet::new();

    for words in hsk_words.values() {
        for word in words {
            // Decompose each character in the word
            for character in word.chars() {
                let char_str = character.to_string();
                let mut visited = HashSet::new();
                let leaves = decompose_to_leaves(&char_str, ids_map, &mut visited);
                allowed_components.extend(leaves);
            }
        }
    }

    allowed_components
}

/// Build complete game data
pub fn build_game_data(
    hsk_words: HashMap<u8, Vec<String>>,
    ids_map: HashMap<String, String>,
) -> GameData {
    println!("🔧 Building character decompositions...");
    let char_to_decomposition = build_char_decompositions(&ids_map);
    println!("  ✅ Built {} character decompositions", char_to_decomposition.len());

    println!("🔧 Building components → characters mapping...");
    let components_to_chars = build_components_to_chars(&char_to_decomposition, &ids_map);
    println!("  ✅ Built {} component combinations", components_to_chars.len());

    println!("🔧 Extracting allowed components from HSK words...");
    let allowed_components = extract_allowed_components(&hsk_words, &ids_map);
    println!("  ✅ Found {} unique leaf components", allowed_components.len());

    GameData {
        char_to_decomposition,
        components_to_chars,
        allowed_components,
        hsk_words,
    }
}

/// Save game data to JSON files
pub fn save_game_data(game_data: &GameData, output_dir: &str) -> Result<()> {
    fs::create_dir_all(output_dir)?;

    // Save character decompositions
    let decomp_path = format!("{}/char_to_decomposition.json", output_dir);
    let mut file = File::create(&decomp_path)?;
    let json = serde_json::to_string_pretty(&game_data.char_to_decomposition)?;
    file.write_all(json.as_bytes())?;
    println!("  ✅ Saved character decompositions to {}", decomp_path);

    // Save components to characters mapping
    let comp_path = format!("{}/components_to_chars.json", output_dir);
    let mut file = File::create(&comp_path)?;
    let json = serde_json::to_string_pretty(&game_data.components_to_chars)?;
    file.write_all(json.as_bytes())?;
    println!("  ✅ Saved components mapping to {}", comp_path);

    // Save allowed components
    let allowed_path = format!("{}/allowed_components.json", output_dir);
    let mut file = File::create(&allowed_path)?;
    let json = serde_json::to_string_pretty(&game_data.allowed_components)?;
    file.write_all(json.as_bytes())?;
    println!("  ✅ Saved allowed components to {}", allowed_path);

    // Save HSK words
    let hsk_path = format!("{}/hsk_words.json", output_dir);
    let mut file = File::create(&hsk_path)?;
    let json = serde_json::to_string_pretty(&game_data.hsk_words)?;
    file.write_all(json.as_bytes())?;
    println!("  ✅ Saved HSK words to {}", hsk_path);

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_components_handles_entity_references() {
        // Test with entity references like &CDP-8B7A;
        let ids = "⿰&CDP-8B7A;攵";
        let components = extract_components_from_ids(ids);

        assert_eq!(components.len(), 2);
        assert_eq!(components[0], "&CDP-8B7A;");
        assert_eq!(components[1], "攵");
    }

    #[test]
    fn test_extract_components_handles_regular_chars() {
        // Test with regular characters
        let ids = "⿰木米";
        let components = extract_components_from_ids(ids);

        assert_eq!(components.len(), 2);
        assert_eq!(components[0], "木");
        assert_eq!(components[1], "米");
    }

    #[test]
    fn test_extract_components_handles_mixed() {
        // Test with mix of entity references and regular chars
        let ids = "⿱&CDP-855B;米";
        let components = extract_components_from_ids(ids);

        assert_eq!(components.len(), 2);
        assert_eq!(components[0], "&CDP-855B;");
        assert_eq!(components[1], "米");
    }

    #[test]
    fn test_extract_components_filters_operators() {
        // Test that IDS operators are filtered out
        let ids = "⿰⿱日月木";
        let components = extract_components_from_ids(ids);

        assert_eq!(components.len(), 3);
        assert_eq!(components[0], "日");
        assert_eq!(components[1], "月");
        assert_eq!(components[2], "木");
    }

    #[test]
    fn test_no_ascii_components_in_decomposition() {
        // Verify that decomposed components don't contain ASCII letters/symbols
        // except for entity references which start with & and end with ;
        let ids = "⿰&CDP-8B7A;攵";
        let components = extract_components_from_ids(ids);

        for component in &components {
            if component.starts_with('&') && component.ends_with(';') {
                // Entity reference - this is OK
                continue;
            }

            // Regular component - should not contain ASCII letters or symbols
            for c in component.chars() {
                assert!(
                    !c.is_ascii_alphanumeric() && c != '&' && c != ';' && c != '-',
                    "Component '{}' contains invalid ASCII character '{}'",
                    component,
                    c
                );
            }
        }
    }
}
