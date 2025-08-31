import React, { useState, useEffect } from 'react';
import { Form, Card, Badge, Spinner, Accordion } from 'react-bootstrap';
import {
  Coins,
  Shield,
  Rocket,
  Crown,
  Heart,
  Zap,
  Wind,
  Waves,
  Flame,
  Snowflake,
  Diamond,
  Gem,
  DollarSign,
  BarChart3,
  TrendingUp,
  Building,
  Activity,
  Target,
  Users,
  Mountain,
  Star,
  Droplets,
  Sun,
  Leaf,
  Globe,
  Cpu,
  Bitcoin
} from 'lucide-react';
import { Market } from '../types/api';

interface MarketSelectorProps {
  markets: Market[];
  selectedMarket: string;
  onMarketChange: (market: string) => void;
  isLoading: boolean;
  defaultMarket?: string;
}

export const MarketSelector: React.FC<MarketSelectorProps> = ({
  markets,
  selectedMarket,
  onMarketChange,
  isLoading,
  defaultMarket
}) => {
  const [selectedCategory, setSelectedCategory] = useState('');

  // Auto-select category and market based on defaultMarket or selectedMarket
  useEffect(() => {
    if (markets.length > 0 && selectedMarket) {
      // Find the market in the list
      const market = markets.find(m => m.symbol === selectedMarket);
      if (market) {
        // Extract category from market name
        const category = market.market.split('_')[0];
        setSelectedCategory(category);
      }
    } else if (defaultMarket && markets.length > 0 && !selectedMarket) {
      // Auto-select from default market
      const market = markets.find(m => m.symbol === defaultMarket);
      if (market) {
        // Extract category from market name
        const category = market.market.split('_')[0];
        setSelectedCategory(category);
        onMarketChange(defaultMarket);
      }
    }
  }, [defaultMarket, markets, selectedMarket, onMarketChange]);

  // Group markets by category
  const groupedMarkets = markets.reduce((acc, market) => {
    const category = market.market.split('_')[0];
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(market);
    return acc;
  }, {} as Record<string, Market[]>);

  // Group markets by subcategory within a category
  const getGroupedMarketsBySubcategory = (category: string) => {
    const categoryMarkets = groupedMarkets[category] || [];
    return categoryMarkets.reduce((acc, market) => {
      const subcategory = market.submarket_display_name || market.submarket || 'Outros';
      if (!acc[subcategory]) {
        acc[subcategory] = [];
      }
      acc[subcategory].push(market);
      return acc;
    }, {} as Record<string, Market[]>);
  };

  // Get market icon based on category with more variety
  const getMarketIcon = (category: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      'forex': <DollarSign className="text-success" size={16} />,
      'indices': <BarChart3 className="text-primary" size={16} />,
      'commodities': <TrendingUp className="text-warning" size={16} />,
      'synthetic_index': <Cpu className="text-danger" size={16} />,
      'synthetic': <Cpu className="text-danger" size={16} />,
      'cryptocurrencies': <Bitcoin className="text-info" size={16} />,
      'cryptocurrency': <Bitcoin className="text-info" size={16} />,
      'stocks': <Building className="text-danger" size={16} />,
      'volatility': <Activity className="text-purple" size={16} />,
      'bear_market': <TrendingUp className="text-danger" size={16} />,
      'bull_market': <TrendingUp className="text-success" size={16} />,
      'step': <Target className="text-info" size={16} />,
      'range_break': <Users className="text-secondary" size={16} />,
      'asian': <Mountain className="text-success" size={16} />,
      'european': <Building className="text-primary" size={16} />,
      'american': <Star className="text-warning" size={16} />,
      'oceania': <Droplets className="text-info" size={16} />,
      'african': <Sun className="text-warning" size={16} />,
      'energy': <Flame className="text-danger" size={16} />,
      'metals': <Target className="text-warning" size={16} />,
      'agricultural': <Leaf className="text-success" size={16} />,
      'derived': <Rocket className="text-purple" size={16} />,
      'major_pairs': <Crown className="text-warning" size={16} />,
      'minor_pairs': <Heart className="text-info" size={16} />,
      'exotic_pairs': <Diamond className="text-success" size={16} />,
      'smart_fx': <Zap className="text-warning" size={16} />,
      'crash_boom': <Flame className="text-danger" size={16} />,
      'turbos': <Wind className="text-success" size={16} />,
      'vanilla': <Snowflake className="text-info" size={16} />,
      'digits': <Target className="text-warning" size={16} />,
      'lookbacks': <Waves className="text-primary" size={16} />,
      'barriers': <Shield className="text-success" size={16} />,
      'high_low': <TrendingUp className="text-info" size={16} />,
      'touch': <Target className="text-warning" size={16} />,
      'asian_handicap': <Mountain className="text-success" size={16} />,
      'call_put_spread': <BarChart3 className="text-primary" size={16} />,
      'other': <Gem className="text-secondary" size={16} />
    };
    
    return iconMap[category] || <Globe className="text-secondary" size={16} />;
  };

  // Get market color variant with more variety
  const getMarketColor = (category: string) => {
    const colorMap: Record<string, string> = {
      'forex': 'success',
      'indices': 'primary',
      'commodities': 'warning',
      'synthetic_index': 'danger',
      'synthetic': 'danger',
      'cryptocurrencies': 'info',
      'cryptocurrency': 'info',
      'stocks': 'danger',
      'volatility': 'purple',
      'bear_market': 'danger',
      'bull_market': 'success',
      'step': 'info',
      'range_break': 'secondary',
      'asian': 'success',
      'european': 'primary',
      'american': 'warning',
      'oceania': 'info',
      'african': 'warning',
      'energy': 'danger',
      'metals': 'warning',
      'agricultural': 'success',
      'derived': 'purple',
      'major_pairs': 'warning',
      'minor_pairs': 'info',
      'exotic_pairs': 'success',
      'smart_fx': 'warning',
      'crash_boom': 'danger',
      'turbos': 'success',
      'vanilla': 'info',
      'digits': 'warning',
      'lookbacks': 'primary',
      'barriers': 'success',
      'high_low': 'info',
      'touch': 'warning',
      'asian_handicap': 'success',
      'call_put_spread': 'primary',
      'other': 'secondary'
    };
    
    return colorMap[category] || 'secondary';
  };

  // Convert to Camel Case
  const toCamelCase = (str: string) => {
    return str
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  // Get category display name with Camel Case
  const getCategoryDisplayName = (category: string) => {
    const nameMap: Record<string, string> = {
      'forex': 'Forex (Moedas)',
      'indices': 'Índices',
      'commodities': 'Commodities',
      'synthetic_index': 'Synthetic Index',
      'synthetic': 'Synthetic',
      'cryptocurrencies': 'Cryptocurrencies',
      'cryptocurrency': 'Cryptocurrency',
      'stocks': 'Ações',
      'volatility': 'Volatilidade',
      'bear_market': 'Bear Market',
      'bull_market': 'Bull Market',
      'step': 'Step',
      'range_break': 'Range Break',
      'asian': 'Mercados Asiáticos',
      'european': 'Mercados Europeus',
      'american': 'Mercados Americanos',
      'oceania': 'Mercados da Oceania',
      'african': 'Mercados Africanos',
      'energy': 'Energia',
      'metals': 'Metais',
      'agricultural': 'Agrícolas',
      'derived': 'Derivados',
      'major_pairs': 'Major Pairs',
      'minor_pairs': 'Minor Pairs',
      'exotic_pairs': 'Exotic Pairs',
      'smart_fx': 'Smart FX',
      'crash_boom': 'Crash Boom',
      'turbos': 'Turbos',
      'vanilla': 'Vanilla',
      'digits': 'Digits',
      'lookbacks': 'Lookbacks',
      'barriers': 'Barriers',
      'high_low': 'High Low',
      'touch': 'Touch',
      'asian_handicap': 'Asian Handicap',
      'call_put_spread': 'Call Put Spread',
      'other': 'Outros'
    };
    
    return nameMap[category] || toCamelCase(category);
  };

  // Handle category change
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    onMarketChange(''); // Reset market selection when category changes
  };

  if (isLoading) {
    return (
      <div className="text-center py-4">
        <Spinner animation="border" variant="primary" />
        <p className="text-muted mt-2">Carregando mercados...</p>
      </div>
    );
  }

  return (
    <div>
      {/* Dependent Selects */}
      <div className="mb-4">
        {/* Category Select */}
        <Form.Group className="mb-3">
          <Form.Label>Selecione uma Categoria</Form.Label>
          <Form.Select
            value={selectedCategory}
            onChange={(e) => handleCategoryChange(e.target.value)}
            className="form-select"
          >
            <option value="">Escolha uma categoria...</option>
            {Object.entries(groupedMarkets).map(([category, categoryMarkets]) => (
              <option key={category} value={category}>
                {getCategoryDisplayName(category)} ({categoryMarkets.length} mercados)
              </option>
            ))}
          </Form.Select>
        </Form.Group>

        {/* Market Select (dependent on category) */}
        {selectedCategory && (
          <Form.Group className="mb-3">
            <Form.Label>Selecione um Mercado</Form.Label>
            <Form.Select
              value={selectedMarket}
              onChange={(e) => onMarketChange(e.target.value)}
              className="form-select"
            >
              <option value="">Escolha um mercado...</option>
              {(() => {
                const subcategoryGroups = getGroupedMarketsBySubcategory(selectedCategory);
                return Object.entries(subcategoryGroups).map(([subcategory, subcategoryMarkets]) => (
                  <optgroup key={subcategory} label={`${subcategory} (${subcategoryMarkets.length})`}>
                    {subcategoryMarkets.map((market) => (
                      <option key={market.symbol} value={market.symbol}>
                        {market.display_name || market.symbol}
                      </option>
                    ))}
                  </optgroup>
                ));
              })()}
            </Form.Select>
          </Form.Group>
        )}
      </div>

      {/* Selected Market Info */}
      {selectedMarket && (
        <Card className="selected-market-card mb-3">
          <Card.Header>
            <h6 className="mb-0">Mercado Selecionado</h6>
          </Card.Header>
          <Card.Body>
            {(() => {
              const market = markets.find(m => m.symbol === selectedMarket);
              if (!market) return null;
              
              const category = market.market.split('_')[0];
              return (
                <div>
                  <div className="d-flex align-items-center mb-2">
                    <div className="me-3">
                      {getMarketIcon(category)}
                    </div>
                    <div className="flex-grow-1">
                      <h6 className="mb-1">{market.market}</h6>
                      <small className="text-muted">{market.symbol}</small>
                    </div>
                    <Badge bg={getMarketColor(category)}>
                      {getCategoryDisplayName(category)}
                    </Badge>
                  </div>
                  {market.display_name && (
                    <div className="mt-2">
                      <small className="text-muted">
                        <strong>Descrição:</strong> {market.display_name}
                      </small>
                    </div>
                  )}
                  {market.submarket_display_name && (
                    <div className="mt-1">
                      <small className="text-muted">
                        <strong>Submercado:</strong> {market.submarket_display_name}
                      </small>
                    </div>
                  )}
                  {market.pip && (
                    <div className="mt-1">
                      <small className="text-muted">
                        <strong>Pip:</strong> {market.pip}
                      </small>
                    </div>
                  )}
                  {market.min_stake && market.max_stake && (
                    <div className="mt-1">
                      <small className="text-muted">
                        <strong>Stake:</strong> {market.min_stake} - {market.max_stake}
                      </small>
                    </div>
                  )}
                </div>
              );
            })()}
          </Card.Body>
        </Card>
      )}

      {/* Market Categories Accordion */}
      <div>
        <h6 className="text-white mb-3">Explorar Categorias</h6>
        <Accordion className="market-accordion">
          {Object.entries(groupedMarkets).map(([category, categoryMarkets], index) => (
            <Accordion.Item key={category} eventKey={index.toString()}>
              <Accordion.Header className="d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center">
                  <div className="me-2">
                    {getMarketIcon(category)}
                  </div>
                  <span className="text-white">{getCategoryDisplayName(category)}</span>
                </div>
                <div className="d-flex align-items-center ms-auto">
                  <Badge bg={getMarketColor(category)} className="me-2">
                    {categoryMarkets.length}
                  </Badge>
                </div>
              </Accordion.Header>
              <Accordion.Body className="p-3">
                {(() => {
                  const subcategoryGroups = getGroupedMarketsBySubcategory(category);
                  const hasMultipleSubcategories = Object.keys(subcategoryGroups).length > 1;
                  
                  if (hasMultipleSubcategories) {
                    // Show subcategories with headers
                    return Object.entries(subcategoryGroups).map(([subcategory, subcategoryMarkets]) => (
                      <div key={subcategory} className="mb-4">
                        <h6 className="text-white mb-3 border-bottom pb-2">
                          {subcategory} ({subcategoryMarkets.length})
                        </h6>
                        <div className="market-categories-grid">
                          {subcategoryMarkets.map((market) => (
                            <Card 
                              key={market.symbol}
                              className="market-category-card"
                              onClick={() => {
                                setSelectedCategory(category);
                                onMarketChange(market.symbol);
                              }}
                            >
                              <Card.Body className="p-2">
                                <div className="d-flex flex-column align-items-center">
                                  <div className="mb-1">
                                    {getMarketIcon(category)}
                                  </div>
                                  <small className="text-muted text-center">
                                    {market.display_name || market.symbol}
                                  </small>
                                  <Badge bg={getMarketColor(category)} className="mt-1 small">
                                    {market.symbol}
                                  </Badge>
                                </div>
                              </Card.Body>
                            </Card>
                          ))}
                        </div>
                      </div>
                    ));
                  } else {
                    // Show all markets without subcategory headers
                    return (
                      <div className="market-categories-grid">
                        {categoryMarkets.map((market) => (
                          <Card 
                            key={market.symbol}
                            className="market-category-card"
                            onClick={() => {
                              setSelectedCategory(category);
                              onMarketChange(market.symbol);
                            }}
                          >
                            <Card.Body className="p-2">
                              <div className="d-flex flex-column align-items-center">
                                <div className="mb-1">
                                  {getMarketIcon(category)}
                                </div>
                                <small className="text-muted text-center">
                                  {market.display_name || market.symbol}
                                </small>
                                <Badge bg={getMarketColor(category)} className="mt-1 small">
                                  {market.symbol}
                                </Badge>
                              </div>
                            </Card.Body>
                          </Card>
                        ))}
                      </div>
                    );
                  }
                })()}
              </Accordion.Body>
            </Accordion.Item>
          ))}
        </Accordion>
      </div>
    </div>
  );
};
