import type { GameData, Card, GameState, Hint } from './types';

let gameData: GameData | null = null;

// Clear cache on module reload (for development)
if (typeof window !== 'undefined') {
	(window as any).__clearGameDataCache = () => {
		gameData = null;
		console.log('🗑️ Game data cache cleared');
	};
}

export async function loadGameData(): Promise<GameData> {
	// Always reload in development to pick up changes
	// if (gameData) {
	// 	console.log('📦 Using cached game data');
	// 	return gameData;
	// }

	console.log('📥 Loading game data...');
	const [charToDecomp, componentsToChars, allowedComponents, hskWords, wordGlosses, charGlosses] = await Promise.all([
		fetch('/game_data/char_to_decomposition.json').then((r) => r.json()),
		fetch('/game_data/components_to_chars.json').then((r) => r.json()),
		fetch('/game_data/allowed_components.json').then((r) => r.json()),
		fetch('/game_data/hsk_words.json').then((r) => r.json()),
		fetch('/game_data/word_glosses.json').then((r) => r.json()).catch((e) => {
			console.warn('⚠️ Failed to load word glosses:', e);
			return {};
		}),
		fetch('/game_data/char_glosses.json').then((r) => r.json()).catch((e) => {
			console.warn('⚠️ Failed to load char glosses:', e);
			return {};
		})
	]);

	console.log('✅ Loaded glosses:', Object.keys(wordGlosses).length, 'words,', Object.keys(charGlosses).length, 'chars');

	gameData = {
		charToDecomposition: charToDecomp,
		componentsToChars,
		allowedComponents,
		hskWords,
		wordGlosses,
		charGlosses
	};

	return gameData;
}

export function getHSKLevel(totalRoundsCompleted: number, roundsPerLevel: number): number {
	const level = Math.floor(totalRoundsCompleted / roundsPerLevel) + 1;
	return Math.min(level, 7); // Cap at HSK 7
}

export function selectRandomWord(hskLevel: number, data: GameData): string {
	const words = data.hskWords[hskLevel.toString()];
	if (!words || words.length === 0) {
		throw new Error(`No words found for HSK level ${hskLevel}`);
	}

	// Filter for single-character words only (more focused learning)
	// Exclude leaf components (would make the game trivial)
	const validWords = words.filter((word) => {
		// Only single characters
		if (word.length !== 1) return false;

		// Single character - check if it's a leaf component
		const decomp = data.charToDecomposition[word];
		if (!decomp) return false; // No decomposition data, skip it

		// If it has components (not a leaf), it's valid
		return decomp.components && decomp.components.length > 0;
	});

	// If no valid single-character words, fall back to all words
	const wordPool = validWords.length > 0 ? validWords : words;
	return wordPool[Math.floor(Math.random() * wordPool.length)];
}

export function decomposeToLeaves(
	character: string,
	data: GameData,
	path: string[] = []
): string[] {
	// Prevent infinite recursion by checking if this character is already in the current path
	if (path.includes(character)) {
		// Circular reference detected, treat as leaf
		return [character];
	}

	const decomp = data.charToDecomposition[character];
	if (!decomp) {
		// This is a leaf component
		return [character];
	}

	const leaves: string[] = [];
	const newPath = [...path, character];

	for (const component of decomp.components) {
		const subLeaves = decomposeToLeaves(component, data, newPath);
		leaves.push(...subLeaves);
	}

	return leaves;
}

export function getComponentsForWord(word: string, data: GameData): string[] {
	const allComponents: string[] = [];

	// Check if this is a single character/entity reference or a multi-character word
	// Entity references like &CDP-89FA; should be treated as a single unit
	// Multi-character words like "你好" should be decomposed character by character
	const isEntityReference = word.startsWith('&') && word.endsWith(';');
	const isSingleChar = word.length === 1 || [...word].length === 1; // Handle multi-byte Unicode

	if (isEntityReference || isSingleChar) {
		// Single character or entity reference - decompose it directly
		const leaves = decomposeToLeaves(word, data);
		allComponents.push(...leaves);
	} else {
		// Multi-character word - decompose each character independently
		for (const char of word) {
			const leaves = decomposeToLeaves(char, data);
			// Add all leaves, including duplicates
			allComponents.push(...leaves);
		}
	}

	return allComponents;
}

/**
 * Get components from target character + 2 decoy characters to make the game more challenging
 * Preserves duplicate components (e.g., if 哥 needs two 可, both are included)
 */
export function getComponentsWithDecoys(
	targetWord: string,
	hskLevel: number,
	data: GameData
): { components: string[]; decoyWords: string[] } {
	const allComponents: string[] = [];
	const decoyWords: string[] = [];

	// Add components from target character (including duplicates)
	const targetComponents = getComponentsForWord(targetWord, data);
	allComponents.push(...targetComponents);

	// Select 2 random decoy CHARACTERS (not words) from the same HSK level
	const levelWords = data.hskWords[hskLevel.toString()] || [];

	// Filter to only single characters that can be decomposed
	const availableDecoyChars = levelWords.filter((w) => {
		if (w === targetWord) return false; // Not the target
		if (w.length !== 1) return false; // Only single characters

		// Must have a decomposition (not a leaf)
		const decomp = data.charToDecomposition[w];
		return decomp && decomp.components && decomp.components.length > 0;
	});

	// Shuffle and pick 2 decoy characters
	const shuffled = [...availableDecoyChars].sort(() => Math.random() - 0.5);
	const selectedDecoys = shuffled.slice(0, 2);

	// Add components from decoy characters (including duplicates)
	for (const decoy of selectedDecoys) {
		const decoyComponents = getComponentsForWord(decoy, data);
		allComponents.push(...decoyComponents);
		decoyWords.push(decoy);
	}

	// IMPORTANT: Remove any component that exactly matches the target character
	// This prevents the answer from being directly available as a component
	const filteredComponents = allComponents.filter((comp) => {
		// Remove if this component IS the entire target character
		return comp !== targetWord;
	});

	// Randomize the order of components
	const shuffledComponents = filteredComponents.sort(() => Math.random() - 0.5);

	return {
		components: shuffledComponents,
		decoyWords
	};
}

export function createCardsFromComponents(components: string[], data: GameData): Card[] {
	return components.map((comp, index) => ({
		id: `${comp}-${index}-${Date.now()}`,
		character: comp,
		isLeaf: !data.charToDecomposition[comp]
	}));
}

/**
 * Build the full decomposition graph showing all paths from current cards to target
 * Returns all valid "next steps" that can be taken with currently available cards
 */
function findValidNextSteps(
	targetWord: string,
	cards: Card[],
	data: GameData
): { cardIds: string[]; result: string; leadsToTarget: boolean }[] {
	const validSteps: { cardIds: string[]; result: string; leadsToTarget: boolean }[] = [];
	const componentsToCharsMap = data.componentsToChars;

	// Build a map of available card characters to their IDs
	const charToCardIds = new Map<string, string[]>();
	cards.forEach((card) => {
		if (!charToCardIds.has(card.character)) {
			charToCardIds.set(card.character, []);
		}
		charToCardIds.get(card.character)!.push(card.id);
	});

	console.log('🔍 Finding valid next steps from available cards:', cards.map(c => c.character));

	// Try all pairs of currently available cards
	for (let i = 0; i < cards.length; i++) {
		for (let j = i + 1; j < cards.length; j++) {
			const comp1 = cards[i].character;
			const comp2 = cards[j].character;
			const sortedKey = [comp1, comp2].sort().join('');
			const possibleResults = componentsToCharsMap[sortedKey] || [];

			// Check each possible result
			for (const result of possibleResults) {
				// Get required components for this result
				const requiredComponents = getComponentsForWord(result, data);
				const selectedChars = [comp1, comp2];

				// Verify we have enough components
				if (hasEnoughComponents(selectedChars, requiredComponents, data)) {
					// Check if this result leads to the target
					const isTarget = result === targetWord;
					const isIntermediate = !isTarget && isPartOfDecomposition(result, targetWord, data);

					if (isTarget || isIntermediate) {
						console.log(`  ✅ Valid step: ${comp1} + ${comp2} → ${result} (${isTarget ? 'TARGET' : 'INTERMEDIATE'})`);
						validSteps.push({
							cardIds: [cards[i].id, cards[j].id],
							result,
							leadsToTarget: true
						});
					}
				}
			}
		}
	}

	// Also try all triplets of currently available cards (for characters that need 3 components)
	for (let i = 0; i < cards.length; i++) {
		for (let j = i + 1; j < cards.length; j++) {
			for (let k = j + 1; k < cards.length; k++) {
				const comp1 = cards[i].character;
				const comp2 = cards[j].character;
				const comp3 = cards[k].character;
				const sortedKey = [comp1, comp2, comp3].sort().join('');
				const possibleResults = componentsToCharsMap[sortedKey] || [];

				// Check each possible result
				for (const result of possibleResults) {
					// Get required components for this result
					const requiredComponents = getComponentsForWord(result, data);
					const selectedChars = [comp1, comp2, comp3];

					// Verify we have enough components
					if (hasEnoughComponents(selectedChars, requiredComponents, data)) {
						// Check if this result leads to the target
						const isTarget = result === targetWord;
						const isIntermediate = !isTarget && isPartOfDecomposition(result, targetWord, data);

						if (isTarget || isIntermediate) {
							console.log(`  ✅ Valid step: ${comp1} + ${comp2} + ${comp3} → ${result} (${isTarget ? 'TARGET' : 'INTERMEDIATE'})`);
							validSteps.push({
								cardIds: [cards[i].id, cards[j].id, cards[k].id],
								result,
								leadsToTarget: true
							});
						}
					}
				}
			}
		}
	}

	console.log(`Found ${validSteps.length} valid next steps that lead to target`);
	return validSteps;
}

/**
 * Generate smart hints that suggest pairs of components that can be combined
 * Only suggests pairs that are currently achievable and lead toward the target
 * Special case: If the target word is already available as a card, just highlight it
 */
export function generateHints(
	targetWord: string,
	cards: Card[],
	data: GameData
): { cardIds: string[]; used: boolean; isAnswer?: boolean }[] {
	console.log('🔍 HINT GENERATION DEBUG for target:', targetWord);
	console.log('Available cards:', cards.map(c => c.character));

	const hints: { cardIds: string[]; used: boolean; isAnswer?: boolean }[] = [];

	// Build a map of card characters to their IDs
	const charToCardIds = new Map<string, string[]>();
	cards.forEach((card) => {
		if (!charToCardIds.has(card.character)) {
			charToCardIds.set(card.character, []);
		}
		charToCardIds.get(card.character)!.push(card.id);
	});

	// SPECIAL CASE: Check if the target word is already available as a single card
	const targetCardIds = charToCardIds.get(targetWord);
	if (targetCardIds && targetCardIds.length > 0) {
		// The answer is already available! Just highlight it
		console.log('✨ Target word is already available as a card!');
		hints.push({
			cardIds: [targetCardIds[0]],
			used: false,
			isAnswer: true
		});
		return hints; // Return immediately with just this hint
	}

	// Get the full decomposition tree for the target
	const targetDecomp = data.charToDecomposition[targetWord];
	console.log('Target decomposition:', targetDecomp);

	// Find all valid next steps based on currently available cards
	const validSteps = findValidNextSteps(targetWord, cards, data);

	// Convert valid steps to hints (up to 3)
	// Prioritize steps that lead directly to the target
	validSteps.sort((a, b) => {
		if (a.result === targetWord && b.result !== targetWord) return -1;
		if (a.result !== targetWord && b.result === targetWord) return 1;
		return 0;
	});

	// Take up to 3 unique hints
	const usedCardPairs = new Set<string>();
	for (const step of validSteps) {
		const pairKey = step.cardIds.sort().join(',');
		if (!usedCardPairs.has(pairKey) && hints.length < 3) {
			console.log(`  Adding hint: ${step.cardIds.length} cards → ${step.result}`);
			hints.push({ cardIds: step.cardIds, used: false });
			usedCardPairs.add(pairKey);
		}
	}

	console.log(`Final hints generated: ${hints.length}`);
	console.log('All hints:', hints.map(h => `${h.cardIds.length} cards`));

	return hints;
}

/**
 * Check if a character is part of the decomposition path to the target
 */
function isPartOfDecomposition(char: string, target: string, data: GameData): boolean {
	const targetDecomp = data.charToDecomposition[target];
	if (!targetDecomp) return false;

	// Check if char is a direct component
	if (targetDecomp.components.includes(char)) return true;

	// Check if char is a component of any component (recursive)
	for (const component of targetDecomp.components) {
		if (isPartOfDecomposition(char, component, data)) {
			return true;
		}
	}

	return false;
}

/**
 * Helper function to check if we have enough of each component
 * For example, if a character needs two 夕, we need to have two 夕 selected
 *
 * IMPORTANT: This function decomposes the selected characters to leaf components first,
 * so if you select '&CDP-89FA;' (which decomposes to [刀, 二]), it will count as having 刀 and 二
 */
function hasEnoughComponents(selectedChars: string[], requiredComponents: string[], data: GameData): boolean {
	// First, decompose all selected chars to their leaf components
	const selectedLeafComponents: string[] = [];
	for (const char of selectedChars) {
		const leaves = decomposeToLeaves(char, data);
		selectedLeafComponents.push(...leaves);
	}

	console.log(`      hasEnoughComponents: selected [${selectedChars.join(', ')}] → leaves [${selectedLeafComponents.join(', ')}]`);
	console.log(`      hasEnoughComponents: required [${requiredComponents.join(', ')}]`);

	// Count occurrences of each component in selected leaf components
	const selectedCounts = new Map<string, number>();
	for (const char of selectedLeafComponents) {
		selectedCounts.set(char, (selectedCounts.get(char) || 0) + 1);
	}

	// Count occurrences of each component in required components
	const requiredCounts = new Map<string, number>();
	for (const char of requiredComponents) {
		requiredCounts.set(char, (requiredCounts.get(char) || 0) + 1);
	}

	// Check if we have enough of each required component
	for (const [char, requiredCount] of requiredCounts) {
		const selectedCount = selectedCounts.get(char) || 0;
		if (selectedCount < requiredCount) {
			console.log(`      hasEnoughComponents: ❌ Need ${requiredCount} of '${char}', only have ${selectedCount}`);
			return false;
		}
	}

	console.log(`      hasEnoughComponents: ✅ Have all required components`);
	return true;
}

export function findPossibleCombinations(
	selectedCards: Card[],
	data: GameData
): string[] {
	if (selectedCards.length === 0) return [];

	const selectedChars = selectedCards.map((c) => c.character);
	const allCombinations = new Set<string>();

	console.log('🔍 findPossibleCombinations called with:', selectedChars);

	// Check all possible subsets of selected cards (including the full set)
	// This allows building intermediate characters like "气" from "𠂉一⺄"
	// before combining with "米" to make "氣"
	const checkSubset = (chars: string[]) => {
		if (chars.length === 0) return;

		const sortedKey = chars.slice().sort().join('');
		const matches = data.componentsToChars[sortedKey];

		if (matches) {
			console.log(`  Checking subset [${chars.join(', ')}] → key: "${sortedKey}" → ${matches.length} potential matches`);
			// For each potential match, verify we have enough of each component
			for (const char of matches) {
				// Get the required components for this character
				const requiredComponents = getComponentsForWord(char, data);

				console.log(`    Candidate: ${char}, requires: [${requiredComponents.join(', ')}]`);

				// Check if our selected chars contain enough of each required component
				if (hasEnoughComponents(chars, requiredComponents, data)) {
					console.log(`      ✅ VALID - adding ${char}`);
					allCombinations.add(char);
				} else {
					console.log(`      ❌ REJECTED - not enough components`);
				}
			}
		}
	};

	// Generate all non-empty subsets
	const n = selectedChars.length;
	for (let i = 1; i < (1 << n); i++) {
		const subset: string[] = [];
		for (let j = 0; j < n; j++) {
			if (i & (1 << j)) {
				subset.push(selectedChars[j]);
			}
		}
		checkSubset(subset);
	}

	return Array.from(allCombinations);
}

export function combineCards(
	selectedCards: Card[],
	targetChar: string,
	availableCards: Card[],
	data: GameData
): Card[] {
	// Remove selected cards
	const remaining = availableCards.filter(
		(card) => !selectedCards.find((sc) => sc.id === card.id)
	);

	// Add new combined card
	const newCard: Card = {
		id: `${targetChar}-combined-${Date.now()}`,
		character: targetChar,
		isLeaf: !data.charToDecomposition[targetChar]
	};

	return [...remaining, newCard];
}

export function decomposeCard(card: Card, availableCards: Card[], data: GameData): Card[] {
	const decomp = data.charToDecomposition[card.character];
	if (!decomp) return availableCards; // Can't decompose a leaf

	// Remove the card being decomposed
	const remaining = availableCards.filter((c) => c.id !== card.id);

	// Add component cards
	const newCards = decomp.components.map((comp, index) => ({
		id: `${comp}-decomp-${index}-${Date.now()}`,
		character: comp,
		isLeaf: !data.charToDecomposition[comp]
	}));

	return [...remaining, ...newCards];
}

export function checkAnswer(availableCards: Card[], targetWord: string): boolean {
	// Get all characters from available cards
	const availableChars = availableCards.map((c) => c.character);

	// Check if we can form the target word from available cards
	// For each character in the target word, we need to have it in available cards
	const targetChars = targetWord.split('');

	// Create a copy of available chars to track usage
	const remainingChars = [...availableChars];

	for (const targetChar of targetChars) {
		const index = remainingChars.indexOf(targetChar);
		if (index === -1) {
			// Target character not found in available cards
			return false;
		}
		// Remove the used character
		remainingChars.splice(index, 1);
	}

	// All target characters were found
	return true;
}

export function initializeGameState(data: GameData): GameState {
	const hskLevel = 1;
	const targetWord = selectRandomWord(hskLevel, data);

	// Get components from 3 words: target + 2 decoys
	const { components, decoyWords } = getComponentsWithDecoys(targetWord, hskLevel, data);
	const cards = createCardsFromComponents(components, data);

	// Get definitions for the target word (join array into string)
	// Use character glosses for single characters (includes top words with underscores)
	const isSingleChar = targetWord.length === 1;
	const definitions = isSingleChar
		? data.charGlosses?.[targetWord]
		: data.wordGlosses?.[targetWord];
	const targetGloss = definitions && definitions.length > 0
		? definitions.join('; ')
		: `Word: ${targetWord}`;

	// Get the decomposition of the target word for debugging
	const targetDecomp = getComponentsForWord(targetWord, data);

	// Generate smart hints
	const hints = generateHints(targetWord, cards, data);

	console.log('🎮 Game initialized:', {
		targetWord,
		targetGloss,
		hasGlosses: !!data.wordGlosses,
		glossCount: data.wordGlosses ? Object.keys(data.wordGlosses).length : 0,
		decoyWords,
		componentCount: components.length,
		allComponents: components,
		targetWordDecomposition: targetDecomp,
		targetWordLength: targetWord.length,
		targetWordChars: targetWord.split(''),
		hintsGenerated: hints.length
	});

	return {
		currentLevel: hskLevel,
		roundsPerLevel: 2,
		currentRound: 1,
		totalRoundsCompleted: 0,
		targetWord,
		targetGloss,
		availableCards: cards,
		selectedCards: [],
		possibleCombinations: [],
		attemptsLeft: 3,
		maxAttempts: 3,
		gameOver: false,
		won: false,
		hints,
		hintsUsed: 0, // Start with 0 hints used this round
		totalHintsUsed: 0 // Start with 0 total hints used
	};
}

/**
 * Regenerate hints based on current available cards
 * This should be called after combining or decomposing cards
 */
export function regenerateHints(state: GameState, data: GameData): GameState {
	const newHints = generateHints(state.targetWord, state.availableCards, data);

	return {
		...state,
		hints: newHints,
		hintsUsed: 0 // Reset hints used counter when regenerating
	};
}

/**
 * Use the next available hint
 * Returns the updated state with the hint marked as used
 */
export function useHint(state: GameState): { state: GameState; hint: Hint | null } {
	const nextHint = state.hints.find((h) => !h.used);
	if (!nextHint) {
		return { state, hint: null };
	}

	// Mark hint as used
	const updatedHints = state.hints.map((h) =>
		h === nextHint ? { ...h, used: true } : h
	);

	return {
		state: {
			...state,
			hints: updatedHints,
			hintsUsed: state.hintsUsed + 1, // Increment hints used this round
			totalHintsUsed: state.totalHintsUsed + 1 // Increment total hints used
		},
		hint: nextHint
	};
}

export function nextRound(state: GameState, data: GameData): GameState {
	const newTotalRounds = state.totalRoundsCompleted + 1;
	const newLevel = getHSKLevel(newTotalRounds, state.roundsPerLevel);
	const newRound = (newTotalRounds % state.roundsPerLevel) + 1;

	const targetWord = selectRandomWord(newLevel, data);

	// Get components from 3 words: target + 2 decoys
	const { components } = getComponentsWithDecoys(targetWord, newLevel, data);
	const cards = createCardsFromComponents(components, data);

	// Get definitions for the target word (join array into string)
	// Use character glosses for single characters (includes top words with underscores)
	const isSingleChar = targetWord.length === 1;
	const definitions = isSingleChar
		? data.charGlosses?.[targetWord]
		: data.wordGlosses?.[targetWord];
	const targetGloss = definitions && definitions.length > 0
		? definitions.join('; ')
		: `Word: ${targetWord}`;

	// Generate smart hints for the new round
	const hints = generateHints(targetWord, cards, data);

	return {
		...state,
		currentLevel: newLevel,
		currentRound: newRound,
		totalRoundsCompleted: newTotalRounds,
		targetWord,
		targetGloss,
		availableCards: cards,
		selectedCards: [],
		possibleCombinations: [],
		attemptsLeft: state.maxAttempts,
		gameOver: false,
		won: false,
		hints,
		hintsUsed: 0, // Reset hints used for new round
		totalHintsUsed: state.totalHintsUsed // Preserve total hints used
	};
}

