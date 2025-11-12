// Simplified main.rs for HSK level analysis and game data generation
mod chinese_types;
mod chinese_char_types;
mod game_data_builder;

use anyhow::{Context, Result};
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader, Write};

use chinese_types::ChineseDictionaryElement;
use chinese_char_types::ChineseCharacter;
use game_data_builder::{load_all_ids, build_game_data, save_game_data};

fn main() -> Result<()> {
    println!("🚀 Starting HSK level analysis and game data generation...");

    println!("📚 Loading Chinese word dictionary...");
    let chinese_words = load_chinese_dictionary("chinese_dictionary_word_2025-06-25.jsonl")
        .context("Failed to load Chinese word dictionary")?;

    println!("📚 Loading Chinese character dictionary...");
    let chinese_chars = load_chinese_char_dictionary("chinese_dictionary_char_2025-06-25.jsonl")
        .context("Failed to load Chinese character dictionary")?;

    // Analyze HSK levels
    analyze_hsk_levels(&chinese_words, &chinese_chars);

    // Extract HSK words by level
    println!("\n🎮 Extracting HSK words for game data...");
    let hsk_words = extract_hsk_words(&chinese_words);

    // Extract word glosses
    println!("\n📖 Extracting word glosses...");
    let word_glosses = extract_word_glosses(&chinese_words);
    println!("  ✅ Extracted {} word glosses", word_glosses.len());

    // Extract character glosses with top words
    println!("\n📖 Extracting character glosses with top words...");
    let char_glosses = extract_char_glosses_with_top_words(&chinese_chars);
    println!("  ✅ Extracted {} character glosses", char_glosses.len());

    // Load IDS data
    println!("\n📖 Loading IDS (character decomposition) data...");
    let ids_map = load_all_ids()
        .context("Failed to load IDS data")?;

    // Build game data
    println!("\n🎮 Building game data structures...");
    let game_data = build_game_data(hsk_words, ids_map);

    // Save game data
    println!("\n💾 Saving game data...");
    save_game_data(&game_data, "game_data")
        .context("Failed to save game data")?;

    // Save word glosses
    save_word_glosses(&word_glosses, "game_data/word_glosses.json")
        .context("Failed to save word glosses")?;

    // Save character glosses
    save_word_glosses(&char_glosses, "game_data/char_glosses.json")
        .context("Failed to save character glosses")?;

    println!("\n✅ All done! Game data saved to game_data/ directory");

    Ok(())
}



fn load_chinese_dictionary(path: &str) -> Result<Vec<ChineseDictionaryElement>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut entries = Vec::new();

    for (line_num, line) in reader.lines().enumerate() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }

        match serde_json::from_str::<ChineseDictionaryElement>(&line) {
            Ok(entry) => entries.push(entry),
            Err(e) => {
                eprintln!("Warning: Failed to parse Chinese entry on line {}: {}", line_num + 1, e);
                continue;
            }
        }

        // Progress indicator
        if (entries.len()) % 10000 == 0 {
            println!("  Loaded {} Chinese entries...", entries.len());
        }
    }

    println!("  ✅ Loaded {} Chinese entries total", entries.len());
    Ok(entries)
}

fn load_chinese_char_dictionary(path: &str) -> Result<Vec<ChineseCharacter>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut entries = Vec::new();

    for line in reader.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }

        match serde_json::from_str::<ChineseCharacter>(&line) {
            Ok(entry) => entries.push(entry),
            Err(_e) => {
                // Silently skip parse errors
                continue;
            }
        }
    }

    println!("  ✅ Loaded {} Chinese character entries", entries.len());
    Ok(entries)
}

fn analyze_hsk_levels(words: &[ChineseDictionaryElement], chars: &[ChineseCharacter]) {
    println!("\n📊 HSK Level Analysis\n");
    println!("{}", "=".repeat(60));

    // Analyze words
    println!("\n🔤 WORD DICTIONARY ANALYSIS:");
    println!("{}", "-".repeat(60));

    let mut word_hsk_counts = vec![0; 11]; // HSK 1-9 + level 10 (no HSK) + no statistics
    let mut words_with_stats = 0;
    let mut words_without_stats = 0;

    for word in words {
        if let Some(ref stats) = word.statistics {
            words_with_stats += 1;
            let level = stats.hsk_level as usize;
            if level <= 10 {
                word_hsk_counts[level] += 1;
            }
        } else {
            words_without_stats += 1;
        }
    }

    println!("Total words: {}", words.len());
    println!("Words with statistics: {}", words_with_stats);
    println!("Words without statistics: {}", words_without_stats);
    println!();

    println!("HSK Level Distribution:");
    for level in 1..=9 {
        if word_hsk_counts[level] > 0 {
            let percentage = (word_hsk_counts[level] as f64 / words_with_stats as f64) * 100.0;
            println!("  HSK {}: {:>6} words ({:>5.2}%)", level, word_hsk_counts[level], percentage);
        }
    }

    let no_hsk = word_hsk_counts[10];
    if no_hsk > 0 {
        let percentage = (no_hsk as f64 / words_with_stats as f64) * 100.0;
        println!("  No HSK (level 10): {:>6} words ({:>5.2}%)", no_hsk, percentage);
    }

    // Analyze characters
    println!("\n📝 CHARACTER DICTIONARY ANALYSIS:");
    println!("{}", "-".repeat(60));

    let mut char_hsk_counts = vec![0; 11]; // HSK 1-9 + level 10 (no HSK) + no statistics
    let mut chars_with_stats = 0;
    let mut chars_without_stats = 0;

    for char_entry in chars {
        if let Some(ref stats) = char_entry.statistics {
            chars_with_stats += 1;
            if let Some(level) = stats.hsk_level {
                let level = level as usize;
                if level <= 10 {
                    char_hsk_counts[level] += 1;
                }
            }
        } else {
            chars_without_stats += 1;
        }
    }

    println!("Total characters: {}", chars.len());
    println!("Characters with statistics: {}", chars_with_stats);
    println!("Characters without statistics: {}", chars_without_stats);
    println!();

    println!("HSK Level Distribution:");
    for level in 1..=9 {
        if char_hsk_counts[level] > 0 {
            let percentage = (char_hsk_counts[level] as f64 / chars_with_stats as f64) * 100.0;
            println!("  HSK {}: {:>6} characters ({:>5.2}%)", level, char_hsk_counts[level], percentage);
        }
    }

    let no_hsk = char_hsk_counts[10];
    if no_hsk > 0 {
        let percentage = (no_hsk as f64 / chars_with_stats as f64) * 100.0;
        println!("  No HSK (level 10): {:>6} characters ({:>5.2}%)", no_hsk, percentage);
    }

    println!("\n{}", "=".repeat(60));
    println!("\n✅ Analysis complete!");
}

fn extract_hsk_words(words: &[ChineseDictionaryElement]) -> HashMap<u8, Vec<String>> {
    let mut hsk_words: HashMap<u8, Vec<String>> = HashMap::new();

    for word in words {
        if let Some(ref stats) = word.statistics {
            let level = stats.hsk_level;

            // Only include HSK levels 1-9 (exclude level 10 which means "no HSK")
            if level >= 1 && level <= 9 {
                hsk_words
                    .entry(level as u8)
                    .or_insert_with(Vec::new)
                    .push(word.trad.clone());
            }
        }
    }

    // Print summary
    for level in 1..=9 {
        if let Some(words) = hsk_words.get(&level) {
            println!("  HSK {}: {} words", level, words.len());
        }
    }

    hsk_words
}

fn extract_word_glosses(words: &[ChineseDictionaryElement]) -> HashMap<String, Vec<String>> {
    let mut glosses = HashMap::new();

    for word in words {
        let mut all_definitions = Vec::new();

        // Collect all definitions from all items
        for item in &word.items {
            if let Some(ref definitions) = item.definitions {
                all_definitions.extend(definitions.clone());
            }
        }

        // Only add if we found at least one definition
        if !all_definitions.is_empty() {
            glosses.insert(word.trad.clone(), all_definitions);
        }
    }

    glosses
}

fn extract_char_glosses_with_top_words(chars: &[ChineseCharacter]) -> HashMap<String, Vec<String>> {
    let mut glosses = HashMap::new();

    for char_entry in chars {
        let mut all_definitions = Vec::new();

        // Add the main gloss if available
        if let Some(ref gloss) = char_entry.gloss {
            all_definitions.push(gloss.clone());
        }

        // Add top 3 words with underscores showing where the character appears
        if let Some(ref stats) = char_entry.statistics {
            if let Some(ref top_words) = stats.top_words {
                for top_word in top_words.iter().take(3) {
                    // Try to replace the character with underscore in the word
                    // Check both simplified (word) and traditional (trad) forms
                    let mut word_with_underscore = top_word.word.replace(&char_entry.char, "_");

                    // If no replacement in simplified, try traditional form
                    if !word_with_underscore.contains('_') && top_word.trad != top_word.word {
                        let trad_with_underscore = top_word.trad.replace(&char_entry.char, "_");
                        if trad_with_underscore.contains('_') {
                            word_with_underscore = trad_with_underscore;
                        }
                    }

                    // If still no underscore, try replacing the variantOf character
                    // (e.g., 龢 is a variant of 和, so replace 和 with _)
                    if !word_with_underscore.contains('_') {
                        if let Some(ref variant_of) = char_entry.variant_of {
                            let variant_replaced = top_word.word.replace(variant_of, "_");
                            if variant_replaced.contains('_') {
                                word_with_underscore = variant_replaced;
                            } else if top_word.trad != top_word.word {
                                let trad_variant_replaced = top_word.trad.replace(variant_of, "_");
                                if trad_variant_replaced.contains('_') {
                                    word_with_underscore = trad_variant_replaced;
                                }
                            }
                        }
                    }

                    // If still no underscore after all attempts, just use _ as fallback
                    if !word_with_underscore.contains('_') {
                        word_with_underscore = String::from("_");
                    }

                    let formatted = format!("{} ({})", word_with_underscore, top_word.gloss);
                    all_definitions.push(formatted);
                }
            }
        }

        // Only add if we found at least one definition
        if !all_definitions.is_empty() {
            glosses.insert(char_entry.char.clone(), all_definitions);
        }
    }

    glosses
}

fn save_word_glosses(glosses: &HashMap<String, Vec<String>>, path: &str) -> Result<()> {
    let mut file = File::create(path)?;
    let json = serde_json::to_string_pretty(glosses)?;
    file.write_all(json.as_bytes())?;
    println!("  ✅ Saved word definitions to {}", path);
    Ok(())
}
