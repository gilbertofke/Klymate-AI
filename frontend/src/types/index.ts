// User Types
export interface User {
  id: number
  email: string
  name?: string
  display_name?: string
  location?: string
  profile_picture_url?: string
  firebase_uid: string
  email_verified: boolean
  eco_score: number
  total_co2_saved: number
  current_streak: number
  onboarding_completed: boolean
  created_at: string
  updated_at: string
}

export interface UserProfile extends User {
  baseline_carbon_footprint?: number
  preferences?: Record<string, any>
  onboarding_data?: OnboardingData
}

// Comprehensive Onboarding Data Types
export interface OnboardingData {
  // Profile Information
  location: string
  household_size: number
  income_level: 'low' | 'medium' | 'high'
  lifestyle_goals: string[]
  privacy_preferences: Record<string, boolean>
  
  // Transportation
  primary_transport: 'car' | 'public_transport' | 'bike' | 'walk' | 'mixed'
  commute_distance: number
  vehicle_type?: 'none' | 'electric' | 'hybrid' | 'gas' | 'diesel'
  public_transport_usage: 'never' | 'rarely' | 'sometimes' | 'often' | 'always'
  travel_frequency: 'low' | 'medium' | 'high'
  transportation_preferences: string[]
  
  // Energy
  home_type: 'apartment' | 'house' | 'condo' | 'other'
  home_size: 'small' | 'medium' | 'large'
  heating_type: 'gas' | 'electric' | 'renewable' | 'mixed'
  cooling_preferences: string[]
  appliance_usage: Record<string, string>
  renewable_energy_interest: boolean
  energy_efficiency_goals: string[]
  
  // Diet
  diet_type: 'omnivore' | 'vegetarian' | 'vegan' | 'pescatarian' | 'flexitarian'
  meal_frequency: number
  meal_patterns: string[]
  food_sourcing_preferences: string[]
  local_food_preference: boolean
  organic_food_preference: boolean
  cooking_habits: string[]
  food_waste_considerations: string[]
  
  // Lifestyle & Consumption
  shopping_frequency: 'minimal' | 'moderate' | 'frequent'
  shopping_habits: string[]
  sustainability_priorities: string[]
  waste_management_practices: string[]
  water_conservation_habits: string[]
  consumption_patterns: Record<string, any>
}

// Authentication Types
export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  expires_at?: number
}

export interface AuthResponse {
  message: string
  user: User
  tokens: AuthTokens
}

export interface LoginCredentials {
  email: string
  password: string
  rememberMe?: boolean
}

export interface RegisterCredentials {
  email: string
  password: string
  name: string
  acceptTerms: boolean
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirm {
  token: string
  newPassword: string
  confirmPassword: string
}

export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

export interface AuthError {
  code: string
  message: string
  field?: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: AuthError | null
}

// Habit Types
export interface HabitCategory {
  id: number
  name: string
  category_type: 'transport' | 'diet' | 'energy' | 'lifestyle'
  description: string
  co2_impact_per_unit: number
  unit: string
  icon?: string
  color?: string
  impact_multiplier?: number
}

export interface Habit {
  id: number
  user_id: number
  category_id: number
  category?: HabitCategory
  action: string
  quantity: number
  co2_saved: number
  notes?: string
  photo_url?: string
  verified: boolean
  logged_at: string
  created_at: string
  updated_at: string
}

export interface HabitCreate {
  category_id: number
  action: string
  quantity: number
  notes?: string
  photo?: File
}

export interface HabitUpdate {
  action?: string
  quantity?: number
  notes?: string
  photo?: File
}

export interface HabitFilters {
  category_id?: number
  start_date?: string
  end_date?: string
  verified?: boolean
  limit?: number
  offset?: number
}

export interface HabitStatistics {
  total_habits: number
  total_co2_saved: number
  current_streak: number
  longest_streak: number
  categories_breakdown: Record<string, number>
  weekly_progress: number[]
  monthly_progress: number
  category_stats: Array<{
    category: string
    count: number
    co2_saved: number
    percentage: number
  }>
}

// AI Coach Types
export interface AIAgent {
  id: string
  name: string
  description: string
  specialization: string
  status: 'active' | 'inactive' | 'maintenance'
  last_activity?: string
  capabilities: string[]
  avatar?: string
  personality_traits?: string[]
}

export interface ChatMessage {
  id: string
  conversation_id: string
  type: 'user' | 'ai'
  content: string
  timestamp: string
  agent_id?: string
  rating?: number
  feedback?: string
  metadata?: Record<string, any>
}

export interface Conversation {
  id: string
  user_id: number
  agent_id: string
  title: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
  tags: string[]
  session_id?: string
}

export interface ChatRequest {
  message: string
  agent_id?: string
  session_id?: string
  include_history?: boolean
  context?: Record<string, any>
}

export interface ConversationSearchRequest {
  query?: string
  agent_id?: string
  limit?: number
  offset?: number
  start_date?: string
  end_date?: string
}

export interface ChatResponse {
  response: string
  session_id: string
  conversation_id: string
  agent_id: string
  model_used: string
  processing_time_ms: number
  context_used: Record<string, any>
  suggestions?: Suggestion[]
}

export interface Suggestion {
  id: string
  title: string
  description: string
  category: 'transport' | 'energy' | 'diet' | 'lifestyle'
  estimated_impact: number
  difficulty: 'easy' | 'medium' | 'hard'
  timeframe: string
  personalized_reason: string
  action_steps: string[]
  confidence_score?: number
}

export interface AIInsight {
  id: string
  user_id: number
  title: string
  description: string
  category: string
  impact_level: 'low' | 'medium' | 'high'
  confidence_score: number
  action_items: string[]
  trends?: Record<string, any>
  recommendations?: Suggestion[]
  created_at: string
  expires_at?: string
}

// Gamification Types
export interface Badge {
  id: number
  name: string
  description: string
  icon: string
  category: string
  criteria: BadgeCriteria
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
  color?: string
  earned?: boolean
  earned_at?: string
  progress?: number
}

export interface BadgeCriteria {
  type: 'habit_count' | 'streak' | 'impact' | 'category_mastery' | 'consistency'
  target: number
  timeframe?: 'daily' | 'weekly' | 'monthly' | 'all_time'
  category?: string
}

export interface UserBadge {
  id: number
  user_id: number
  badge_id: number
  badge?: Badge
  earned_at: string
  progress_data?: Record<string, any>
}

export interface LeaderboardEntry {
  user_id: number
  display_name: string
  eco_score: number
  total_co2_saved: number
  rank: number
  badge_count: number
  avatar?: string
  is_current_user?: boolean
}

export interface GamificationStats {
  eco_score: number
  eco_score_trend: number
  current_streak: number
  longest_streak: number
  total_badges: number
  recent_badges: Badge[]
  leaderboard_position: number
  points_to_next_level: number
  level: number
}

// Dashboard Types
export interface DashboardMetrics {
  co2_saved: number
  co2_saved_trend: number
  active_agents: number
  energy_optimized: number
  energy_efficiency: number
  carbon_credits: number
  credits_earning_rate: number
  habits_this_week: number
  current_streak: number
}

export interface DashboardData {
  user: User
  metrics: DashboardMetrics
  active_agents: AIAgent[]
  recent_activity: Activity[]
  quick_stats: {
    total_co2_saved: number
    habits_this_month: number
    badges_earned: number
    leaderboard_position: number
  }
  generated_at: string
}

// Analytics Types
export interface TrendData {
  period: string
  value: number
  category?: string
  comparison?: number
  percentage_change?: number
}

export interface CategoryAnalytics {
  category: string
  current_value: number
  trend: number
  percentage: number
  recommendations: string[]
  impact_potential: number
}

export interface UserComparison {
  user_value: number
  average_value: number
  percentile: number
  region: string
  demographic: string
  improvement_potential: number
}

export interface PerformanceMetrics {
  efficiency_score: number
  consistency_score: number
  impact_score: number
  overall_score: number
  period_days: number
  trends: {
    efficiency: number
    consistency: number
    impact: number
  }
}

export interface AnalyticsDashboard {
  user_id: number
  period_days: number
  carbon_footprint_trends: TrendData[]
  category_breakdown: CategoryAnalytics[]
  user_comparisons: UserComparison
  performance_metrics: PerformanceMetrics
  projections: {
    monthly_co2_savings: number
    yearly_impact: number
    goal_progress: number
  }
  generated_at: string
}

// Carbon Credits Types
export interface CarbonCredits {
  current_balance: number
  total_earned: number
  total_redeemed: number
  pending_verification: number
  estimated_usd_value: number
  earning_rate: number
  projected_earnings: number
}

export interface CreditTransaction {
  id: string
  user_id: number
  transaction_type: 'earned' | 'redeemed' | 'bonus' | 'penalty'
  amount: number
  amount_usd?: number
  source: string
  description: string
  status: 'pending' | 'verified' | 'completed' | 'failed'
  created_at: string
  verified_at?: string
  metadata?: Record<string, any>
}

export interface ExchangeRates {
  credits_to_usd: number
  last_updated: string
  market_trend: 'up' | 'down' | 'stable'
  trend_percentage: number
}

export interface RedemptionOption {
  id: string
  name: string
  description: string
  category: 'donation' | 'offset' | 'product' | 'service'
  cost: number
  availability: 'available' | 'limited' | 'unavailable'
  image_url?: string
  provider: string
  impact_description?: string
}

export interface RedemptionRequest {
  redemption_option_id: string
  amount: number
  recipient_info?: Record<string, any>
  notes?: string
}

// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total_count: number
  page: number
  per_page: number
  has_more: boolean
}

// Activity and Notification Types
export interface Activity {
  id: string
  user_id: number
  type: 'habit_logged' | 'badge_earned' | 'ai_insight' | 'credits_earned' | 'milestone_reached' | 'agent_interaction'
  title: string
  description: string
  icon: string
  color: string
  timestamp: string
  impact?: number
  category?: string
  metadata?: Record<string, any>
}

export interface Notification {
  id: string
  user_id: number
  type: 'achievement' | 'reminder' | 'insight' | 'credit' | 'system'
  title: string
  message: string
  read: boolean
  action_url?: string
  created_at: string
  expires_at?: string
}

// Error Types
export interface ApiError {
  message: string
  code?: string
  details?: Record<string, any>
}

// Loading States
export interface LoadingState {
  isLoading: boolean
  error: string | null
}

// Navigation Types
export interface NavItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  current?: boolean
  badge?: number
}