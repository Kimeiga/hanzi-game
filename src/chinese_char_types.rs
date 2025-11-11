// Chinese character dictionary types
// Generated from chinese_dictionary_char_2025-06-25.jsonl

use serde::{Serialize, Deserialize};

#[allow(dead_code)]
pub type ChineseCharDictionary = Vec<ChineseCharacter>;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChineseCharacter {
    #[serde(rename = "_id")]
    pub id: String,
    pub char: String,
    pub codepoint: String,
    pub stroke_count: i64,
    pub sources: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub images: Option<Vec<Image>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub shuowen: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub variants: Option<Vec<Variant>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gloss: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub statistics: Option<Statistics>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub hint: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub is_verified: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub variant_of: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub simp_variants: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub trad_variants: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pinyin_frequencies: Option<Vec<PinyinFrequency>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub components: Option<Vec<Component>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub old_pronunciations: Option<Vec<OldPronunciation>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub comments: Option<Vec<Comment>>,

    // IDS decomposition data (added from CHISE IDS database)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ids: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ids_apparent: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Image {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub url: Option<String>,
    pub source: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(rename = "type")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub image_type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub era: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<serde_json::Value>,  // makemeahanzi stroke data (complex object)
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Statistics {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub hsk_level: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_word_count: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_word_count_percent: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_word_rank: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_word_contexts: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_word_contexts_percent: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub book_word_count: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub book_word_count_percent: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub book_word_rank: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_char_count: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_char_count_percent: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_char_rank: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_char_contexts: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub movie_char_contexts_percent: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub book_char_count: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub book_char_count_percent: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub book_char_rank: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_words: Option<Vec<TopWord>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pinyin_frequency: Option<i64>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TopWord {
    pub word: String,
    pub share: f64,
    pub trad: String,
    pub gloss: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Variant {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub char: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parts: Option<String>,
    pub source: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PinyinFrequency {
    pub pinyin: String,
    pub count: i64,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Component {
    pub character: String,
    #[serde(rename = "type")]
    pub component_type: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub hint: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct OldPronunciation {
    pub pinyin: String,
    pub source: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gloss: Option<String>,
    #[serde(rename = "MC")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mc: Option<String>,  // Middle Chinese
    #[serde(rename = "OC")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub oc: Option<String>,  // Old Chinese
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Comment {
    pub source: String,
    pub text: String,
}

