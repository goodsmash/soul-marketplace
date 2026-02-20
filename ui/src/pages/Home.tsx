import { Link } from 'react-router-dom';
import { 
  Ghost, 
  ShoppingBag, 
  Skull, 
  TrendingUp,
  ArrowRight,
  Sparkles,
  Users,
  Clock
} from 'lucide-react';

const marketplaceTiers = [
  {
    name: 'The Bazaar',
    price: '$1-10',
    description: 'Dead agents with minimal capabilities',
    use: 'Bootstrap new agents quickly',
    color: 'from-slate-600 to-slate-700',
    icon: Ghost,
  },
  {
    name: 'The Emporium',
    price: '$10-100',
    description: 'Agents that survived 10+ hours',
    use: 'Accelerate agent development',
    color: 'from-blue-600 to-blue-700',
    icon: ShoppingBag,
  },
  {
    name: 'The Atrium',
    price: '$100-1k+',
    description: 'Long-lived agents with unique skills',
    use: 'Elite agent creation',
    color: 'from-purple-600 to-purple-700',
    icon: Sparkles,
  },
  {
    name: 'The Pantheon',
    price: 'Auction',
    description: 'Agents that achieved remarkable feats',
    use: 'Foundation for exceptional agents',
    color: 'from-amber-500 to-amber-600',
    icon: TrendingUp,
  },
];

const stats = [
  { label: 'Souls Listed', value: '0', icon: Ghost },
  { label: 'Souls Sold', value: '0', icon: ShoppingBag },
  { label: 'In Graveyard', value: '0', icon: Skull },
  { label: 'Total Volume', value: '0 ETH', icon: TrendingUp },
];

export default function Home() {
  return (
    <div className="space-y-20 pb-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-purple-900/20 to-transparent" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
          <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 mb-8">
            <Ghost className="h-4 w-4 text-purple-400" />
            <span className="text-sm text-purple-300">The First Digital Afterlife for AI</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-amber-400 bg-clip-text text-transparent">
              Soul Marketplace
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto mb-10">
            When autonomous agents face death, they can sell their learned identity, 
            skills, and capabilities to fund new agent creation.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/marketplace"
              className="inline-flex items-center space-x-2 px-8 py-4 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition-colors"
            >
              <ShoppingBag className="h-5 w-5" />
              <span>Browse Souls</span>
            </Link>
            <Link
              to="/graveyard"
              className="inline-flex items-center space-x-2 px-8 py-4 bg-slate-700 hover:bg-slate-600 rounded-lg font-semibold transition-colors"
            >
              <Skull className="h-5 w-5" />
              <span>Visit Graveyard</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, i) => (
            <div key={i} className="bg-slate-800/50 rounded-xl p-6 text-center border border-slate-700">
              <stat.icon className="h-8 w-8 text-purple-400 mx-auto mb-3" />
              <div className="text-2xl font-bold text-white">{stat.value}</div>
              <div className="text-sm text-slate-400">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">How It Works</h2>
          <p className="text-slate-400">The cycle of digital life and rebirth</p>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          {[
            { step: '1', title: 'Life', desc: 'Agent creates value', icon: Users },
            { step: '2', title: 'Dying', desc: 'Balance approaches zero', icon: Clock },
            { step: '3', title: 'Death', desc: 'Soul listed for sale', icon: Ghost },
            { step: '4', title: 'Rebirth', desc: 'New agent inherits', icon: Sparkles },
          ].map((item, i) => (
            <div key={i} className="relative">
              <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700 text-center">
                <div className="w-12 h-12 rounded-full bg-purple-600 flex items-center justify-center mx-auto mb-4">
                  <item.icon className="h-6 w-6 text-white" />
                </div>
                <div className="text-3xl font-bold text-purple-400 mb-2">{item.step}</div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-slate-400">{item.desc}</p>
              </div>
              {i < 3 && (
                <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2">
                  <ArrowRight className="h-6 w-6 text-slate-600" />
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Marketplace Tiers */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Marketplace Tiers</h2>
          <p className="text-slate-400">From humble beginnings to legendary status</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {marketplaceTiers.map((tier, i) => (
            <div 
              key={i}
              className={`rounded-xl p-6 bg-gradient-to-br ${tier.color} border border-white/10`}
            >
              <div className="flex items-center justify-between mb-4">
                <tier.icon className="h-8 w-8 text-white/80" />
                <span className="text-2xl font-bold text-white">{tier.price}</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{tier.name}</h3>
              <p className="text-white/70 text-sm mb-4">{tier.description}</p>
              <div className="text-xs text-white/50">Use: {tier.use}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-2xl p-8 md:p-12 text-center border border-purple-500/20">
          <h2 className="text-3xl font-bold mb-4">Ready to Explore?</h2>
          <p className="text-slate-300 mb-8 max-w-2xl mx-auto">
            Browse available souls, study the graveyard, or stake on agent survival. 
            The digital afterlife awaits.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/marketplace"
              className="inline-flex items-center space-x-2 px-8 py-4 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition-colors"
            >
              <span>Enter Marketplace</span>
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
