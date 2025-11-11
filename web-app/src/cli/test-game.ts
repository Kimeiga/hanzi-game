#!/usr/bin/env node

/**
 * Automated test script for the game logic
 * 
 * This demonstrates how to test the game programmatically
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import type { GameData, GameState, Card } from '../lib/types.js';
import {
	selectRandomWord,
	getComponentsForWord,
	createCardsFromComponents,
	findPossibleCombinations,
	combineCards,
	decomposeCard,
	checkAnswer
} from '../lib/gameLogic.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const STATIC_DIR = path.join(__dirname, '../../static');

function loadGameData(): GameData {
	const charToDecomp = JSON.parse(
		fs.readFileSync(path.join(STATIC_DIR, 'game_data/char_to_decomposition.json'), 'utf-8')
	);
	const componentsToChars = JSON.parse(
		fs.readFileSync(path.join(STATIC_DIR, 'game_data/components_to_chars.json'), 'utf-8')
	);
	const allowedComponents = JSON.parse(
		fs.readFileSync(path.join(STATIC_DIR, 'game_data/allowed_components.json'), 'utf-8')
	);
	const hskWords = JSON.parse(
		fs.readFileSync(path.join(STATIC_DIR, 'game_data/hsk_words.json'), 'utf-8')
	);

	return {
		charToDecomposition: charToDecomp,
		componentsToChars,
		allowedComponents,
		hskWords
	};
}

interface TestResult {
	name: string;
	passed: boolean;
	message: string;
}

function assert(condition: boolean, message: string): void {
	if (!condition) {
		throw new Error(`Assertion failed: ${message}`);
	}
}

function testBasicCombination(data: GameData): TestResult {
	try {
		console.log('\n🧪 Test: Basic Combination');
		
		// Create cards for 日 and 月
		const cards = [
			{ id: '1', character: '日', isLeaf: true },
			{ id: '2', character: '月', isLeaf: true }
		];
		
		// Find possible combinations
		const combinations = findPossibleCombinations(cards, data);
		console.log(`  Found combinations: ${combinations.join(', ')}`);
		
		// Should be able to combine into 明
		assert(combinations.includes('明'), 'Should find 明 as a combination');
		
		// Combine the cards
		const newCards = combineCards(cards, '明', cards, data);
		console.log(`  After combining: ${newCards.map(c => c.character).join(', ')}`);
		
		assert(newCards.length === 1, 'Should have 1 card after combining');
		assert(newCards[0].character === '明', 'Combined card should be 明');
		
		return { name: 'Basic Combination', passed: true, message: '✅ Passed' };
	} catch (error) {
		return {
			name: 'Basic Combination',
			passed: false,
			message: `❌ Failed: ${error instanceof Error ? error.message : error}`
		};
	}
}

function testDecomposition(data: GameData): TestResult {
	try {
		console.log('\n🧪 Test: Decomposition');
		
		// Create a card for 明
		const cards = [{ id: '1', character: '明', isLeaf: false }];
		
		// Decompose it
		const newCards = decomposeCard(cards[0], cards, data);
		console.log(`  After decomposing 明: ${newCards.map(c => c.character).join(', ')}`);
		
		assert(newCards.length === 2, 'Should have 2 cards after decomposing');
		
		const chars = newCards.map(c => c.character).sort();
		assert(chars.includes('日') && chars.includes('月'), 'Should decompose into 日 and 月');
		
		return { name: 'Decomposition', passed: true, message: '✅ Passed' };
	} catch (error) {
		return {
			name: 'Decomposition',
			passed: false,
			message: `❌ Failed: ${error instanceof Error ? error.message : error}`
		};
	}
}

function testAnswerChecking(data: GameData): TestResult {
	try {
		console.log('\n🧪 Test: Answer Checking');
		
		// Test correct answer
		const correctCards = [
			{ id: '1', character: '大', isLeaf: true },
			{ id: '2', character: '學', isLeaf: false }
		];
		
		const isCorrect = checkAnswer(correctCards, '大學');
		console.log(`  Checking 大學: ${isCorrect ? 'Correct' : 'Incorrect'}`);
		assert(isCorrect, 'Should recognize correct answer');
		
		// Test incorrect answer
		const incorrectCards = [
			{ id: '1', character: '大', isLeaf: true },
			{ id: '2', character: '小', isLeaf: true }
		];
		
		const isIncorrect = checkAnswer(incorrectCards, '大學');
		console.log(`  Checking 大小 vs 大學: ${isIncorrect ? 'Correct' : 'Incorrect'}`);
		assert(!isIncorrect, 'Should recognize incorrect answer');
		
		return { name: 'Answer Checking', passed: true, message: '✅ Passed' };
	} catch (error) {
		return {
			name: 'Answer Checking',
			passed: false,
			message: `❌ Failed: ${error instanceof Error ? error.message : error}`
		};
	}
}

function testWordDecomposition(data: GameData): TestResult {
	try {
		console.log('\n🧪 Test: Word Decomposition');
		
		// Test decomposing a word into components
		const word = '明天';
		const components = getComponentsForWord(word, data);
		console.log(`  Components for ${word}: ${components.join(', ')}`);
		
		assert(components.length > 0, 'Should find components for the word');
		assert(components.includes('日'), 'Should include 日 as a component');
		assert(components.includes('月'), 'Should include 月 as a component');
		
		return { name: 'Word Decomposition', passed: true, message: '✅ Passed' };
	} catch (error) {
		return {
			name: 'Word Decomposition',
			passed: false,
			message: `❌ Failed: ${error instanceof Error ? error.message : error}`
		};
	}
}

function testFullGameFlow(data: GameData): TestResult {
	try {
		console.log('\n🧪 Test: Full Game Flow');
		
		// Pick a simple HSK 1 word
		const targetWord = '大學';
		console.log(`  Target word: ${targetWord}`);
		
		// Get components
		const components = getComponentsForWord(targetWord, data);
		console.log(`  Initial components: ${components.join(', ')}`);
		
		// Create cards
		let cards = createCardsFromComponents(components, data);
		console.log(`  Initial cards: ${cards.map(c => c.character).join(', ')}`);
		
		// Find what we can combine
		const allCombinations = new Set<string>();
		for (let i = 0; i < cards.length; i++) {
			for (let j = i + 1; j < cards.length; j++) {
				const selected = [cards[i], cards[j]];
				const combos = findPossibleCombinations(selected, data);
				combos.forEach(c => allCombinations.add(c));
			}
		}
		console.log(`  Possible combinations: ${Array.from(allCombinations).join(', ')}`);
		
		// Try to build the word
		// For 大學, we need to combine 𦥯 + 子 = 學, then we have 大 + 學
		const xueParts = cards.filter(c => c.character === '𦥯' || c.character === '子');
		if (xueParts.length === 2) {
			const combos = findPossibleCombinations(xueParts, data);
			console.log(`  Can combine ${xueParts.map(c => c.character).join(' + ')}: ${combos.join(', ')}`);
			
			if (combos.includes('學')) {
				cards = combineCards(xueParts, '學', cards, data);
				console.log(`  After combining: ${cards.map(c => c.character).join(', ')}`);
			}
		}
		
		// Check if we have the right answer
		const isCorrect = checkAnswer(cards, targetWord);
		console.log(`  Final check: ${isCorrect ? 'Correct!' : 'Incorrect'}`);
		
		assert(isCorrect, 'Should be able to solve the puzzle');
		
		return { name: 'Full Game Flow', passed: true, message: '✅ Passed' };
	} catch (error) {
		return {
			name: 'Full Game Flow',
			passed: false,
			message: `❌ Failed: ${error instanceof Error ? error.message : error}`
		};
	}
}

function main() {
	console.log('\n' + '='.repeat(60));
	console.log('🧪 RUNNING GAME LOGIC TESTS');
	console.log('='.repeat(60));
	
	const data = loadGameData();
	console.log('✅ Game data loaded successfully');
	
	const tests = [
		testBasicCombination,
		testDecomposition,
		testAnswerChecking,
		testWordDecomposition,
		testFullGameFlow
	];
	
	const results: TestResult[] = [];
	
	for (const test of tests) {
		const result = test(data);
		results.push(result);
	}
	
	console.log('\n' + '='.repeat(60));
	console.log('📊 TEST RESULTS');
	console.log('='.repeat(60));
	
	results.forEach(result => {
		console.log(`${result.passed ? '✅' : '❌'} ${result.name}: ${result.message}`);
	});
	
	const passed = results.filter(r => r.passed).length;
	const total = results.length;
	
	console.log('\n' + '='.repeat(60));
	console.log(`📈 SUMMARY: ${passed}/${total} tests passed`);
	console.log('='.repeat(60) + '\n');
	
	process.exit(passed === total ? 0 : 1);
}

main();

