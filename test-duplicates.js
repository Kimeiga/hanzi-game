// Test script to verify duplicate components are preserved
import fs from 'fs';

// Load game data
const charToDecomp = JSON.parse(fs.readFileSync('game_data/char_to_decomposition.json', 'utf8'));

// Manually implement decomposeToLeaves to test (using path-based recursion prevention)
function decomposeToLeaves(character, charToDecomp, path = []) {
    // Prevent infinite recursion by checking if this character is already in the current path
    if (path.includes(character)) {
        // Circular reference detected, treat as leaf
        return [character];
    }

    const decomp = charToDecomp[character];
    if (!decomp) {
        // This is a leaf
        return [character];
    }

    const leaves = [];
    const newPath = [...path, character];

    // Recursively decompose each component
    for (const component of decomp.components) {
        const subLeaves = decomposeToLeaves(component, charToDecomp, newPath);
        leaves.push(...subLeaves);
    }

    return leaves;
}

// Test 哥
console.log('\n🧪 Testing 哥 (should have duplicate components):');
console.log('Decomposition:', charToDecomp['哥']);

const components = decomposeToLeaves('哥', charToDecomp);
console.log('Leaf components:', components);
console.log('Total count:', components.length);

// Count occurrences
const counts = {};
components.forEach(c => {
    counts[c] = (counts[c] || 0) + 1;
});
console.log('Component counts:', counts);

// Expected: 2x &CDP-8974; and 2x 口
const expected = {
    '&CDP-8974;': 2,
    '口': 2
};

console.log('\n✅ Expected:', expected);
console.log('📊 Actual:', counts);

if (JSON.stringify(counts) === JSON.stringify(expected)) {
    console.log('\n✅ TEST PASSED: Duplicates are preserved!');
} else {
    console.log('\n❌ TEST FAILED: Duplicates not preserved correctly');
}

// Test 的哥
console.log('\n\n🧪 Testing 的哥 (2-character word):');
const word = '的哥';
const allComponents = [];
for (const char of word) {
    const leaves = decomposeToLeaves(char, charToDecomp);
    allComponents.push(...leaves);
}

console.log('All components:', allComponents);
console.log('Total count:', allComponents.length);

const wordCounts = {};
allComponents.forEach(c => {
    wordCounts[c] = (wordCounts[c] || 0) + 1;
});
console.log('Component counts:', wordCounts);

