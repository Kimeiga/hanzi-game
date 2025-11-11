#!/usr/bin/env node

/**
 * CLI tool for testing the Chinese character game logic
 * 
 * Usage:
 *   pnpm cli new [game-id]           - Start a new game
 *   pnpm cli show [game-id]          - Show current game state
 *   pnpm cli select [game-id] <ids>  - Select cards by ID (comma-separated)
 *   pnpm cli combine [game-id] <char> - Combine selected cards into character
 *   pnpm cli decompose [game-id] <id> - Decompose a card by ID
 *   pnpm cli submit [game-id]        - Submit current answer
 *   pnpm cli reset [game-id]         - Reset to new game
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import type { GameData, GameState, Card } from '../lib/types.js';
import {
	getHSKLevel,
	selectRandomWord,
	getComponentsForWord,
	createCardsFromComponents,
	findPossibleCombinations,
	combineCards,
	decomposeCard,
	checkAnswer,
	nextRound
} from '../lib/gameLogic.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const GAMES_DIR = path.join(__dirname, '../../.games');
const STATIC_DIR = path.join(__dirname, '../../static');

// Ensure games directory exists
if (!fs.existsSync(GAMES_DIR)) {
	fs.mkdirSync(GAMES_DIR, { recursive: true });
}

interface PersistedGameState extends GameState {
	gameId: string;
	createdAt: string;
	lastModified: string;
}

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

function getGamePath(gameId: string): string {
	return path.join(GAMES_DIR, `${gameId}.json`);
}

function saveGame(state: PersistedGameState): void {
	const gamePath = getGamePath(state.gameId);
	state.lastModified = new Date().toISOString();
	fs.writeFileSync(gamePath, JSON.stringify(state, null, 2));
	console.log(`\n💾 Game saved: ${gamePath}`);
}

function loadGame(gameId: string): PersistedGameState {
	const gamePath = getGamePath(gameId);
	if (!fs.existsSync(gamePath)) {
		throw new Error(`Game not found: ${gameId}`);
	}
	return JSON.parse(fs.readFileSync(gamePath, 'utf-8'));
}

function initializeGameState(gameId: string, data: GameData): PersistedGameState {
	const hskLevel = 1;
	const targetWord = selectRandomWord(hskLevel, data);
	const components = getComponentsForWord(targetWord, data);
	const cards = createCardsFromComponents(components, data);

	return {
		gameId,
		createdAt: new Date().toISOString(),
		lastModified: new Date().toISOString(),
		currentLevel: hskLevel,
		roundsPerLevel: 2,
		currentRound: 1,
		totalRoundsCompleted: 0,
		targetWord,
		targetGloss: `Word: ${targetWord}`,
		availableCards: cards,
		selectedCards: [],
		possibleCombinations: [],
		attemptsLeft: 3,
		maxAttempts: 3,
		gameOver: false,
		won: false
	};
}

function displayGameState(state: PersistedGameState): void {
	console.log('\n' + '='.repeat(60));
	console.log(`🎮 GAME: ${state.gameId}`);
	console.log('='.repeat(60));
	console.log(`📚 HSK Level: ${state.currentLevel} | Round: ${state.currentRound}/${state.roundsPerLevel}`);
	console.log(`🎯 Target: ${state.targetGloss}`);
	console.log(`💪 Attempts Left: ${state.attemptsLeft}/${state.maxAttempts}`);
	
	if (state.gameOver) {
		console.log(`\n❌ GAME OVER! Answer was: ${state.targetWord}`);
	} else if (state.won) {
		console.log(`\n🎉 YOU WON!`);
	}

	console.log('\n📇 AVAILABLE CARDS:');
	state.availableCards.forEach((card, idx) => {
		const leafMarker = card.isLeaf ? '🌿' : '🔧';
		console.log(`  [${idx}] ${card.character} ${leafMarker} (id: ${card.id})`);
	});

	if (state.selectedCards.length > 0) {
		console.log('\n✅ SELECTED CARDS:');
		state.selectedCards.forEach((card, idx) => {
			console.log(`  [${idx}] ${card.character} (id: ${card.id})`);
		});

		if (state.possibleCombinations.length > 0) {
			console.log('\n🔀 POSSIBLE COMBINATIONS:');
			state.possibleCombinations.forEach((combo, idx) => {
				console.log(`  [${idx}] ${combo}`);
			});
		}
	}

	console.log('\n' + '='.repeat(60));
	console.log(`📅 Created: ${state.createdAt}`);
	console.log(`🕐 Modified: ${state.lastModified}`);
	console.log('='.repeat(60) + '\n');
}

function cmdNew(gameId: string = `game-${Date.now()}`): void {
	console.log(`\n🎮 Creating new game: ${gameId}`);
	const data = loadGameData();
	const state = initializeGameState(gameId, data);
	saveGame(state);
	displayGameState(state);
}

function cmdShow(gameId: string): void {
	const state = loadGame(gameId);
	displayGameState(state);
}

function cmdSelect(gameId: string, cardIndices: string): void {
	const state = loadGame(gameId);
	const data = loadGameData();
	
	const indices = cardIndices.split(',').map(s => parseInt(s.trim()));
	const selectedCards: Card[] = [];
	
	for (const idx of indices) {
		if (idx < 0 || idx >= state.availableCards.length) {
			console.error(`❌ Invalid card index: ${idx}`);
			return;
		}
		selectedCards.push(state.availableCards[idx]);
	}
	
	state.selectedCards = selectedCards;
	state.possibleCombinations = findPossibleCombinations(selectedCards, data);
	
	saveGame(state);
	displayGameState(state);
}

function cmdCombine(gameId: string, targetChar: string): void {
	const state = loadGame(gameId);
	const data = loadGameData();
	
	if (state.selectedCards.length === 0) {
		console.error('❌ No cards selected!');
		return;
	}
	
	state.availableCards = combineCards(
		state.selectedCards,
		targetChar,
		state.availableCards,
		data
	);
	
	state.selectedCards = [];
	state.possibleCombinations = [];
	
	console.log(`\n✨ Combined into: ${targetChar}`);
	saveGame(state);
	displayGameState(state);
}

function cmdDecompose(gameId: string, cardIndex: string): void {
	const state = loadGame(gameId);
	const data = loadGameData();
	
	const idx = parseInt(cardIndex);
	if (idx < 0 || idx >= state.availableCards.length) {
		console.error(`❌ Invalid card index: ${idx}`);
		return;
	}
	
	const card = state.availableCards[idx];
	if (card.isLeaf) {
		console.error(`❌ Cannot decompose leaf component: ${card.character}`);
		return;
	}
	
	state.availableCards = decomposeCard(card, state.availableCards, data);
	state.selectedCards = [];
	state.possibleCombinations = [];
	
	console.log(`\n🔨 Decomposed: ${card.character}`);
	saveGame(state);
	displayGameState(state);
}

function cmdSubmit(gameId: string): void {
	const state = loadGame(gameId);
	const data = loadGameData();
	
	const isCorrect = checkAnswer(state.availableCards, state.targetWord);
	
	if (isCorrect) {
		console.log('\n🎉 CORRECT! Moving to next round...');
		const newState = nextRound(state, data);
		const persistedState: PersistedGameState = {
			...newState,
			gameId: state.gameId,
			createdAt: state.createdAt,
			lastModified: new Date().toISOString()
		};
		saveGame(persistedState);
		displayGameState(persistedState);
	} else {
		state.attemptsLeft--;
		if (state.attemptsLeft <= 0) {
			state.gameOver = true;
			console.log(`\n❌ GAME OVER! The answer was: ${state.targetWord}`);
		} else {
			console.log(`\n❌ Incorrect! ${state.attemptsLeft} attempts left`);
		}
		saveGame(state);
		displayGameState(state);
	}
}

function cmdReset(gameId: string): void {
	const data = loadGameData();
	const state = initializeGameState(gameId, data);
	saveGame(state);
	console.log('\n🔄 Game reset!');
	displayGameState(state);
}

function main() {
	const args = process.argv.slice(2);
	const command = args[0];
	
	if (!command) {
		console.log(`
Chinese Character Game CLI

Usage:
  pnpm cli new [game-id]           - Start a new game
  pnpm cli show <game-id>          - Show current game state
  pnpm cli select <game-id> <ids>  - Select cards by index (comma-separated)
  pnpm cli combine <game-id> <char> - Combine selected cards into character
  pnpm cli decompose <game-id> <idx> - Decompose a card by index
  pnpm cli submit <game-id>        - Submit current answer
  pnpm cli reset <game-id>         - Reset to new game

Examples:
  pnpm cli new test1
  pnpm cli show test1
  pnpm cli select test1 0,1,2
  pnpm cli combine test1 明
  pnpm cli decompose test1 0
  pnpm cli submit test1
		`);
		process.exit(0);
	}
	
	try {
		switch (command) {
			case 'new':
				cmdNew(args[1]);
				break;
			case 'show':
				cmdShow(args[1]);
				break;
			case 'select':
				cmdSelect(args[1], args[2]);
				break;
			case 'combine':
				cmdCombine(args[1], args[2]);
				break;
			case 'decompose':
				cmdDecompose(args[1], args[2]);
				break;
			case 'submit':
				cmdSubmit(args[1]);
				break;
			case 'reset':
				cmdReset(args[1]);
				break;
			default:
				console.error(`Unknown command: ${command}`);
				process.exit(1);
		}
	} catch (error) {
		console.error(`\n❌ Error: ${error instanceof Error ? error.message : error}`);
		process.exit(1);
	}
}

main();

