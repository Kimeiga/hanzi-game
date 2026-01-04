const fs = require('fs');

const kanjiDetails = JSON.parse(fs.readFileSync('static/game_data/kanji_details.json', 'utf8'));
const semanticGraph = JSON.parse(fs.readFileSync('static/game_data/hanzi_semantic_graph.json', 'utf8'));
const jlptKanji = JSON.parse(fs.readFileSync('static/game_data/jlpt_kanji.json', 'utf8'));
const joyoKanji = JSON.parse(fs.readFileSync('static/game_data/joyo_kanji.json', 'utf8'));

// Build semantic map (char -> {category, subcategory, keyword, meaning})
const semanticMap = {};
function buildSemanticMap(node, category = '', subcategory = '') {
  if (node.char) {
    semanticMap[node.char] = { category, subcategory, keyword: node.keyword, meaning: node.meaning };
    if (node.simp) semanticMap[node.simp] = { category, subcategory, keyword: node.keyword, meaning: node.meaning };
  }
  if (node.children) {
    for (const child of node.children) {
      if (child.char) {
        buildSemanticMap(child, category, subcategory || node.name);
      } else {
        buildSemanticMap(child, node.name === 'Hanzi Universe' ? category : node.name, subcategory);
      }
    }
  }
}
buildSemanticMap(semanticGraph);

// Check for issues
const allJlptKanji = [...jlptKanji.N5, ...jlptKanji.N4, ...jlptKanji.N3, ...jlptKanji.N2, ...jlptKanji.N1];

// 1. Check kanji missing from semantic graph
const missingFromSemantic = allJlptKanji.filter(k => !semanticMap[k]);
if (missingFromSemantic.length > 0) {
  console.log('=== JLPT KANJI MISSING FROM SEMANTIC GRAPH ===');
  console.log(missingFromSemantic.join(', '));
}

// 2. Check kanji missing from kanji_details
const missingDetails = allJlptKanji.filter(k => !kanjiDetails[k]);
if (missingDetails.length > 0) {
  console.log('\n=== JLPT KANJI MISSING FROM KANJI_DETAILS ===');
  console.log(missingDetails.join(', '));
}

// 3. Sample check for gloss comparison N5
console.log('\n=== N5 GLOSS COMPARISON ===');
for (const k of jlptKanji.N5) {
  const detail = kanjiDetails[k];
  const semantic = semanticMap[k];
  if (detail && semantic) {
    console.log(`${k}: Detail='${detail.meaning}' | Semantic='${semantic.keyword}' [${semantic.category}>${semantic.subcategory}]`);
  } else if (detail && !semantic) {
    console.log(`${k}: Detail='${detail.meaning}' | Semantic=MISSING`);
  }
}

// 4. Check Joyo coverage
const joyoMissingSemantic = joyoKanji.filter(k => !semanticMap[k]);
const joyoMissingDetails = joyoKanji.filter(k => !kanjiDetails[k]);
console.log(`\n=== JOYO COVERAGE ===`);
console.log(`Total Joyo: ${joyoKanji.length}`);
console.log(`Missing from semantic: ${joyoMissingSemantic.length}`);
console.log(`Missing from details: ${joyoMissingDetails.length}`);
if (joyoMissingSemantic.length > 0) {
  console.log('Missing semantic:', joyoMissingSemantic.join(', '));
}
if (joyoMissingDetails.length > 0) {
  console.log('Missing details:', joyoMissingDetails.join(', '));
}

