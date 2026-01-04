import type { MnemonicGameData, MnemonicQuestion, MnemonicGameState } from './mnemonicTypes';

let mnemonicData: MnemonicGameData | null = null;

/**
 * Load game data and generate component name mappings
 */
export async function loadMnemonicData(): Promise<MnemonicGameData> {
	console.log('📥 Loading mnemonic game data...');
	const [charToDecomp, componentsToChars, allowedComponents, hskWords, wordGlosses, charGlosses, curatedNames] = await Promise.all([
		fetch('/game_data/char_to_decomposition.json').then((r) => r.json()),
		fetch('/game_data/components_to_chars.json').then((r) => r.json()),
		fetch('/game_data/allowed_components.json').then((r) => r.json()),
		fetch('/game_data/hsk_words.json').then((r) => r.json()),
		fetch('/game_data/word_glosses.json').then((r) => r.json()).catch(() => ({})),
		fetch('/game_data/char_glosses.json').then((r) => r.json()).catch(() => ({})),
		fetch('/game_data/curated_component_names.json').then((r) => r.json()).catch(() => ({}))
	]);

	// Generate unique component names, using curated names when available
	const componentNames = generateComponentNames(allowedComponents, charGlosses, curatedNames);

	mnemonicData = {
		charToDecomposition: charToDecomp,
		componentsToChars,
		allowedComponents,
		hskWords,
		wordGlosses,
		charGlosses,
		componentNames
	};

	console.log('✅ Mnemonic data loaded with', Object.keys(componentNames).length, 'component names');
	console.log('📝 Using', Object.keys(curatedNames).filter(k => !k.startsWith('_')).length, 'curated component names');
	return mnemonicData;
}

/**
 * Generate unique English names for each component
 * Uses curated names first, then glosses, then radicals as fallback
 */
function generateComponentNames(
	components: string[],
	charGlosses: Record<string, string[]>,
	curatedNames: Record<string, string> = {}
): Record<string, string> {
	const names: Record<string, string> = {};
	const usedNames = new Map<string, number>(); // Track name usage for disambiguation

	// Common radical names (for components without good glosses)
	const radicalNames: Record<string, string> = {
		'口': 'mouth', '日': 'sun', '月': 'moon', '水': 'water', '氵': 'water',
		'火': 'fire', '灬': 'fire', '木': 'wood', '金': 'metal', '土': 'earth',
		'人': 'person', '亻': 'person', '女': 'woman', '子': 'child', '心': 'heart',
		'忄': 'heart', '手': 'hand', '扌': 'hand', '目': 'eye', '耳': 'ear',
		'言': 'speech', '讠': 'speech', '足': 'foot', '⻊': 'foot', '刀': 'knife',
		'刂': 'knife', '力': 'power', '大': 'big', '小': 'small', '山': 'mountain',
		'石': 'stone', '田': 'field', '禾': 'grain', '米': 'rice', '竹': 'bamboo',
		'艹': 'grass', '⻀': 'grass', '虫': 'insect', '鳥': 'bird', '魚': 'fish',
		'馬': 'horse', '犬': 'dog', '犭': 'dog', '牛': 'cow', '羊': 'sheep',
		'生': 'life', '死': 'death', '王': 'king', '玉': 'jade', '貝': 'shell',
		'見': 'see', '門': 'gate', '雨': 'rain', '風': 'wind', '雲': 'cloud',
		'宀': 'roof', '广': 'shelter', '厂': 'cliff', '冖': 'cover', '冂': 'borders',
		'囗': 'enclosure', '一': 'one', '二': 'two', '三': 'three', '十': 'ten',
		'百': 'hundred', '千': 'thousand', '上': 'up', '下': 'down', '中': 'center',
		'白': 'white', '黑': 'black', '赤': 'red', '青': 'blue', '黃': 'yellow',
		'⺈': 'knife-top', '⺌': 'small-top', '⺍': 'bead', '⺡': 'water-left',
		'⺤': 'claw', '⺧': 'ram', '⺪': 'net', '⺫': 'eye-top', '⺭': 'spirit',
		'⺮': 'bamboo', '⺳': 'fire-dots', '⺶': 'sheep', '⺷': 'sheep-top',
		'⺼': 'meat', '⻌': 'walk', '⻏': 'city-right', '⻖': 'hill-left',
		'⻗': 'rain-top', '⻤': 'ghost', '衤': 'clothes', '礻': 'spirit',
		'辶': 'walk', '飠': 'food', '⺗': 'heart-bottom', '彳': 'step',
		'阝': 'mound', '攵': 'strike', '攴': 'tap', '疒': 'sickness',
		'癶': 'footsteps', '歹': 'death', '殳': 'weapon', '毋': 'mother',
		'比': 'compare', '片': 'slice', '斤': 'axe', '匕': 'spoon',
		'巾': 'cloth', '彡': 'hair', '夂': 'go-slow', '夊': 'go',
		'走': 'walk', '行': 'move', '立': 'stand', '辛': 'bitter',
		'酉': 'wine', '豆': 'bean', '豕': 'pig', '革': 'leather'
	};

	for (const comp of components) {
		let baseName: string;

		// 1. Try curated names first (these are hand-picked unique names)
		if (curatedNames[comp] && !curatedNames[comp].startsWith('_')) {
			baseName = curatedNames[comp];
			// Curated names are already unique, use directly
			names[comp] = baseName;
			continue;
		}
		// 2. Try radical names
		else if (radicalNames[comp]) {
			baseName = radicalNames[comp];
		}
		// 3. Try gloss data
		else if (charGlosses[comp] && charGlosses[comp].length > 0) {
			// Get the first gloss and extract the main meaning
			const gloss = charGlosses[comp][0];
			baseName = extractMainMeaning(gloss);
		}
		// 4. Fall back to character itself or descriptive name
		else {
			baseName = `[${comp}]`;
		}

		// Make the name unique if needed (for non-curated names)
		const count = usedNames.get(baseName) || 0;
		usedNames.set(baseName, count + 1);

		if (count > 0) {
			names[comp] = `${baseName}-${count + 1}`;
		} else {
			names[comp] = baseName;
		}
	}

	return names;
}

/**
 * Extract the main meaning from a gloss string
 * E.g., "mouth" from "mouth, _ (mouth), 出_ (an exit)"
 */
function extractMainMeaning(gloss: string): string {
	// Remove parenthetical notes and underscores
	let meaning = gloss.replace(/_/g, '').replace(/\([^)]*\)/g, '').trim();
	// Take first word if multiple
	meaning = meaning.split(/[,;]/)[0].trim();
	// Clean up and lowercase
	meaning = meaning.toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim();
	// Take just first few words to keep it short
	const words = meaning.split(/\s+/).slice(0, 2);
	return words.join('-') || 'component';
}

/**
 * Decompose a character to its leaf components
 */
function decomposeToLeaves(
	character: string,
	data: MnemonicGameData,
	path: string[] = []
): string[] {
	if (path.includes(character)) {
		return [character];
	}

	const decomp = data.charToDecomposition[character];
	if (!decomp || !decomp.components || decomp.components.length === 0) {
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

/**
 * Select a random word from the HSK level that has decomposable characters
 */
function selectRandomWord(hskLevel: number, data: MnemonicGameData): string {
	const words = data.hskWords[hskLevel.toString()];
	if (!words || words.length === 0) {
		throw new Error(`No words found for HSK level ${hskLevel}`);
	}

	// Filter for single characters that have decompositions
	const validWords = words.filter((word) => {
		if (word.length !== 1) return false;
		const decomp = data.charToDecomposition[word];
		return decomp && decomp.components && decomp.components.length > 0;
	});

	const pool = validWords.length > 0 ? validWords : words;
	return pool[Math.floor(Math.random() * pool.length)];
}

/**
 * Generate a mnemonic question for a character
 */
export function generateQuestion(
	character: string,
	data: MnemonicGameData
): MnemonicQuestion {
	// Get the leaf components
	const components = decomposeToLeaves(character, data);

	// Get English names for each component
	const componentNames = components.map(comp =>
		data.componentNames[comp] || `[${comp}]`
	);

	// Build the equation string
	const equation = componentNames.join(' + ');

	// Get the meaning from glosses
	const glosses = data.charGlosses?.[character] || [];
	const targetMeaning = glosses.length > 0
		? extractMainMeaning(glosses[0])
		: character;

	return {
		targetCharacter: character,
		targetMeaning,
		components,
		componentNames,
		equation
	};
}

/**
 * Check if the user's answer matches the target meaning
 * Uses fuzzy matching to be forgiving of minor differences
 */
export function checkAnswer(userAnswer: string, question: MnemonicQuestion, data: MnemonicGameData): boolean {
	const normalized = userAnswer.toLowerCase().trim();
	const target = question.targetMeaning.toLowerCase().trim();

	// Exact match
	if (normalized === target) return true;

	// Check against all glosses for this character
	const glosses = data.charGlosses?.[question.targetCharacter] || [];
	for (const gloss of glosses) {
		const meaning = extractMainMeaning(gloss).toLowerCase();
		if (normalized === meaning) return true;
		// Partial match - if user's answer contains the meaning or vice versa
		if (normalized.includes(meaning) || meaning.includes(normalized)) return true;
	}

	return false;
}

/**
 * Get HSK level from total rounds completed
 */
function getHSKLevel(totalRoundsCompleted: number, roundsPerLevel: number): number {
	const level = Math.floor(totalRoundsCompleted / roundsPerLevel) + 1;
	return Math.min(level, 7);
}

/**
 * Initialize a new mnemonic game state
 */
export function initializeMnemonicGame(data: MnemonicGameData): MnemonicGameState {
	const hskLevel = 1;
	const character = selectRandomWord(hskLevel, data);
	const question = generateQuestion(character, data);

	console.log('🎯 Mnemonic game initialized:', {
		character: question.targetCharacter,
		meaning: question.targetMeaning,
		equation: question.equation,
		components: question.components
	});

	return {
		currentLevel: hskLevel,
		currentRound: 1,
		totalRoundsCompleted: 0,
		roundsPerLevel: 3,
		currentQuestion: question,
		userAnswer: '',
		attemptsLeft: 3,
		maxAttempts: 3,
		gameOver: false,
		won: false,
		score: 0,
		streak: 0,
		showAnswer: false,
		feedback: null
	};
}

/**
 * Advance to the next round
 */
export function nextRound(state: MnemonicGameState, data: MnemonicGameData): MnemonicGameState {
	const newTotalRounds = state.totalRoundsCompleted + 1;
	const newLevel = getHSKLevel(newTotalRounds, state.roundsPerLevel);
	const newRound = (newTotalRounds % state.roundsPerLevel) + 1;

	const character = selectRandomWord(newLevel, data);
	const question = generateQuestion(character, data);

	return {
		...state,
		currentLevel: newLevel,
		currentRound: newRound,
		totalRoundsCompleted: newTotalRounds,
		currentQuestion: question,
		userAnswer: '',
		attemptsLeft: state.maxAttempts,
		gameOver: false,
		won: false,
		showAnswer: false,
		feedback: null
	};
}

