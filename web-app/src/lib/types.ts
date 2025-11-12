export interface CharacterDecomposition {
	character: string;
	ids: string;
	components: string[];
}

export interface GameData {
	charToDecomposition: Record<string, CharacterDecomposition>;
	componentsToChars: Record<string, string[]>;
	allowedComponents: string[];
	hskWords: Record<string, string[]>;
	wordGlosses?: Record<string, string[]>; // Array of definitions for words
	charGlosses?: Record<string, string[]>; // Array of definitions for characters (includes top words)
}

export interface Card {
	id: string;
	character: string;
	isLeaf: boolean;
}

export interface Hint {
	cardIds: string[]; // IDs of cards to highlight (usually 2, or 1 if isAnswer is true)
	used: boolean; // Whether this hint has been used
	isAnswer?: boolean; // True if this hint is highlighting the final answer (single card)
}

export interface GameState {
	currentLevel: number; // HSK level 1-7, then stays at 7
	roundsPerLevel: number; // 2 rounds per level
	currentRound: number; // Current round within the level
	totalRoundsCompleted: number; // Total rounds completed across all levels
	targetWord: string;
	targetGloss: string;
	availableCards: Card[];
	selectedCards: Card[];
	possibleCombinations: string[];
	attemptsLeft: number;
	maxAttempts: number;
	gameOver: boolean;
	won: boolean;
	hints: Hint[]; // All available hints (no cap)
	hintsUsed: number; // Number of hints used this round
	totalHintsUsed: number; // Total hints used across all rounds
}

