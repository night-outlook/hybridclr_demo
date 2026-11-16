#pragma once
// R03 B2 test-only radix index. Not referenced by native IL2CPP or Player.
// Compressed binary Patricia trie: two nodes per distinct opaque handle
// (one leaf, at most one branch) and <= pointer-width branch decisions.
// No hash collision scan and no handle/owner dereference. Prepare() is the
// ONLY allocation; all subsequent operations are bounded and allocation-free.
#include <cstddef>
#include <cstdint>
#include <memory>
#include <new>

namespace r03_b2_typedef_capacity_candidates {

class BoundedHandlePatriciaIndex final {
public:
    static const size_t kMaxCapacity=1024;
    static const size_t kKeyBits=sizeof(uintptr_t)*8u;
    static const size_t kMaxLookupVisits=kKeyBits+1u;
    static const size_t kMaxInsertVisits=2u*kMaxLookupVisits;
private:
    static_assert(kKeyBits<=64u,"Only 32/64-bit opaque pointer keys supported");
    struct Node {
        uintptr_t key=0;            // leaf key only; never dereferenced
        uint16_t child[2]{};        // one-based node offsets
        uint16_t row=0;             // payload index for leaf only
        uint8_t bit=static_cast<uint8_t>(kKeyBits); // ==kKeyBits for leaf
    };
    std::unique_ptr<Node[]> nodes_{};
    size_t capacity_=0, usedNodes_=0, leaves_=0;
    uint16_t root_=0;

    static uint8_t Direction(uintptr_t key,size_t bit) noexcept {
        return static_cast<uint8_t>(
            (key>>(kKeyBits-1u-bit)) & static_cast<uintptr_t>(1u));
    }
    bool LeafAt(uintptr_t key,uint16_t& leaf,size_t& visits) const noexcept {
        visits=0;leaf=0;
        if(!nodes_ || !key || !root_)return false;
        uint16_t at=root_;
        while(at && visits<kMaxLookupVisits) {
            ++visits;
            if(static_cast<size_t>(at)>usedNodes_)return false;
            const Node& node=nodes_[at];
            if(node.bit==kKeyBits){leaf=at;return true;}
            if(node.bit>=kKeyBits)return false;
            at=node.child[Direction(key,node.bit)];
        }
        return false; // malformed index never becomes positive evidence
    }
public:
    BoundedHandlePatriciaIndex() noexcept=default;
    ~BoundedHandlePatriciaIndex() noexcept{Release();}
    BoundedHandlePatriciaIndex(const BoundedHandlePatriciaIndex&)=delete;
    BoundedHandlePatriciaIndex& operator=(const BoundedHandlePatriciaIndex&)=delete;
    bool Prepare(size_t capacity) noexcept {
        if(nodes_ || !capacity || capacity>kMaxCapacity)return false;
        // Node 0 is absent. N leaves require at most 2*N-1 live nodes.
        nodes_.reset(new(std::nothrow) Node[2u*capacity]());
        if(!nodes_)return false;
        capacity_=capacity;root_=0;usedNodes_=leaves_=0;return true;
    }
    size_t ReservedBytes() const noexcept {
        return 2u*capacity_*sizeof(Node);
    }
    size_t NodeCapacity() const noexcept{return 2u*capacity_;}
    size_t Count() const noexcept{return leaves_;}
    bool Find(uintptr_t key,size_t& row,size_t& visits) const noexcept {
        row=0;
        uint16_t leaf=0;
        if(!LeafAt(key,leaf,visits))return false;
        if(nodes_[leaf].key!=key)return false;
        row=nodes_[leaf].row;return true;
    }
    bool Insert(uintptr_t key,size_t row,size_t& visits) noexcept {
        visits=0;
        if(!nodes_ || !key || row>=capacity_ ||
           leaves_==capacity_)return false;
        if(!root_) {
            ++usedNodes_;
            Node& leaf=nodes_[usedNodes_];
            leaf.key=key;leaf.row=static_cast<uint16_t>(row);
            leaf.bit=static_cast<uint8_t>(kKeyBits);
            root_=static_cast<uint16_t>(usedNodes_);
            ++leaves_;return true;
        }
        uint16_t oldLeaf=0;
        if(!LeafAt(key,oldLeaf,visits))return false;
        const uintptr_t oldKey=nodes_[oldLeaf].key;
        if(oldKey==key)return false; // a caller must handle duplicates via Find
        size_t split=0;
        while(split<kKeyBits && Direction(key,split)==Direction(oldKey,split))
            ++split;
        if(split==kKeyBits || usedNodes_+2u>2u*capacity_-1u)return false;

        // Descend only through smaller split bits. Existing Patricia branch
        // bits strictly increase down every path (MSB first). One new split
        // branch is inserted above the subtree with this differing prefix.
        uint16_t* link=&root_;
        while(*link && nodes_[*link].bit<split) {
            ++visits;
            const Node& node=nodes_[*link];
            if(node.bit>=kKeyBits || visits>kMaxInsertVisits)return false;
            link=&nodes_[*link].child[Direction(key,node.bit)];
        }
        if(!*link || visits>kMaxInsertVisits)return false;
        const uint16_t existing=*link;
        const uint16_t newLeaf=static_cast<uint16_t>(++usedNodes_);
        const uint16_t newBranch=static_cast<uint16_t>(++usedNodes_);
        nodes_[newLeaf].key=key;
        nodes_[newLeaf].row=static_cast<uint16_t>(row);
        nodes_[newLeaf].bit=static_cast<uint8_t>(kKeyBits);
        Node& branch=nodes_[newBranch];
        branch.bit=static_cast<uint8_t>(split);
        const uint8_t dir=Direction(key,split);
        branch.child[dir]=newLeaf;
        branch.child[1u-dir]=existing;
        *link=newBranch;
        ++leaves_;
        return true;
    }
    void Clear() noexcept {
        if(nodes_)
            for(size_t i=0;i<2u*capacity_;++i)nodes_[i]=Node{};
        root_=0;usedNodes_=leaves_=0;
    }
    void Release() noexcept {
        Clear();nodes_.reset();capacity_=0;
    }
};
} // r03_b2_typedef_capacity_candidates
