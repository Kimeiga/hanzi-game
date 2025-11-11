// Example code that deserializes and serializes the model.
// extern crate serde;
// #[macro_use]
// extern crate serde_derive;
// extern crate serde_json;
//
// use generated_module::ChineseDictionary;
//
// fn main() {
//     let json = r#"{"answer": 42}"#;
//     let model: ChineseDictionary = serde_json::from_str(&json).unwrap();
// }

use serde::{Serialize, Deserialize};

#[allow(dead_code)]
pub type ChineseDictionary = Vec<ChineseDictionaryElement>;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChineseDictionaryElement {
    #[serde(rename = "_id")]
    pub id: String,
    pub simp: String,
    pub trad: String,
    pub items: Vec<Item>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gloss: Option<String>,
    pub pinyin_search_string: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub statistics: Option<Statistics>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Item {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source: Option<Source>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub pinyin: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub simp_trad: Option<SimpTrad>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub definitions: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tang: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub variant_refs: Option<Vec<String>>,  // NEW: Variant references for this pronunciation
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum SimpTrad {
    Both,
    Simp,
    Trad,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum Source {
    Cedict,
    #[serde(rename = "dong-chinese")]
    DongChinese,
    Unicode,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Statistics {
    pub hsk_level: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_words: Option<Vec<TopWord>>,
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
    pub pinyin_frequency: Option<i64>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TopWord {
    pub word: String,
    pub share: f64,
    pub trad: String,
    pub gloss: String,
}
