// Types for the Mnemonic Equation Game
// Player sees component names combined (like "mouth + life + sword + big")
// and must answer with the character's meaning (like "eat")

export interface MnemonicGameData {
	charToDecomposition: Record<string, CharacterDecomposition>;
	componentsToChars: Record<string, string[]>;
	allowedComponents: string[];
	hskWords: Record<string, string[]>;
	wordGlosses?: Record<string, string[]>;
	charGlosses?: Record<string, string[]>;
	// Component name mappings - unique English names for each component
	componentNames: Record<string, string>;
}

export interface CharacterDecomposition {
	character: string;
	ids: string;
	components: string[];
}

export interface MnemonicQuestion {
	targetCharacter: string; // The Chinese character (e.g., "喫")
	targetMeaning: string; // The meaning to guess (e.g., "eat")
	components: string[]; // The component characters (e.g., ["口", "生", "刀", "大"])
	componentNames: string[]; // The component English names (e.g., ["mouth", "life", "knife", "big"])
	equation: string; // The formatted equation (e.g., "mouth + life + knife + big")
}

export interface MnemonicGameState {
	currentLevel: number; // HSK level 1-7
	currentRound: number;
	totalRoundsCompleted: number;
	roundsPerLevel: number;
	currentQuestion: MnemonicQuestion;
	userAnswer: string;
	attemptsLeft: number;
	maxAttempts: number;
	gameOver: boolean;
	won: boolean;
	score: number;
	streak: number; // Consecutive correct answers
	showAnswer: boolean; // Show the answer after game over
	feedback: string | null; // Feedback message
}

